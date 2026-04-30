import streamlit as st
import pandas as pd
import sqlite3
import requests
from geopy.distance import geodesic
from streamlit_folium import st_folium
import folium

# =============================
# DATABASE SETUP
# =============================
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
''')

conn.commit()

# =============================
# FUNCTIONS
# =============================
def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def register_user(username, password):
    c.execute("INSERT INTO users VALUES (?,?)", (username, password))
    conn.commit()

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(layout="wide")

# =============================
# LOGIN SYSTEM
# =============================
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    st.title("Register")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Register"):
        register_user(user, pwd)
        st.success("Account created! Go to login")

elif choice == "Login":
    st.title("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        result = login_user(user, pwd)

        if result:
            st.success("Login Successful ✅")

            # =============================
            # MAIN APP STARTS
            # =============================
            data = pd.read_csv("data.csv")

            st.title("🌍 Smart Travel Planner")

            state = st.selectbox("State", data["state"].unique())
            state_data = data[data["state"] == state]

            district = st.selectbox("District", state_data["district"].unique())
            district_data = state_data[state_data["district"] == district]

            taluk = st.selectbox("Taluk", district_data["taluk"].unique())
            final_data = district_data[district_data["taluk"] == taluk]

            # =============================
            # TRAVEL INPUT
            # =============================
            st.subheader("Travel Details")

            start = st.text_input("Starting Location")
            end = st.text_input("Destination")

            vehicle = st.selectbox("Vehicle", ["Car", "Bike", "Bus", "Auto"])
            mileage = st.number_input("Mileage (km/l)", 10, 50, 20)
            fuel_price = st.number_input("Fuel Price", 80, 120, 100)

            budget = st.slider("Budget", 0, 5000, 2000)

            # =============================
            # GET COORDINATES
            # =============================
            def get_coordinates(place):
                url = f"https://nominatim.openstreetmap.org/search?q={place}&format=json"
                res = requests.get(url).json()
                if res:
                    return float(res[0]['lat']), float(res[0]['lon'])
                return None, None

            if st.button("Plan Trip"):

                # =============================
                # MAP
                # =============================
                st.subheader("Live Map")

                start_coord = get_coordinates(start)
                end_coord = get_coordinates(end)

                if start_coord[0] and end_coord[0]:
                    m = folium.Map(location=start_coord, zoom_start=7)

                    folium.Marker(start_coord, tooltip="Start").add_to(m)
                    folium.Marker(end_coord, tooltip="End").add_to(m)

                    folium.PolyLine([start_coord, end_coord]).add_to(m)

                    st_folium(m, width=700, height=400)

                    # =============================
                    # DISTANCE
                    # =============================
                    distance = geodesic(start_coord, end_coord).km

                    st.success(f"Distance: {distance:.2f} km")

                    fuel_needed = distance / mileage
                    cost = fuel_needed * fuel_price

                    st.success(f"Travel Cost: ₹{cost:.2f}")

                else:
                    st.error("Location not found")

                # =============================
                # FILTER DATA
                # =============================
                filtered = final_data[final_data["price"] <= budget]

                # =============================
                # AI RECOMMENDATION (SMART SORT)
                # =============================
                st.subheader("Recommended Places")

                recommended = filtered.sort_values(by=["rating", "price"], ascending=[False, True])

                for _, row in recommended.iterrows():
                    st.write(f"{row['place']} ⭐{row['rating']} ₹{row['price']}")

                # =============================
                # ITINERARY
                # =============================
                st.subheader("Itinerary")

                places = recommended["place"].tolist()

                plan = []

                for i in range(min(3, len(places))):
                    text = f"Day {i+1}: Visit {places[i]}"
                    plan.append(text)
                    st.write(text)

                if plan:
                    st.download_button("Download Plan", "\n".join(plan), "plan.txt")

        else:
            st.error("Invalid login")