import streamlit as st
import pandas as pd

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(page_title="IVIS", layout="wide")

# =============================
# LOAD DATA
# =============================
data = pd.read_csv("data.csv")

# =============================
# TITLE
# =============================
st.title("🌍 Intelligent Voyage Itinerary System")
st.markdown("### Smart Travel Planner (India)")

# =============================
# LOCATION SELECTION
# =============================
col1, col2, col3 = st.columns(3)

with col1:
    state = st.selectbox("Select State", data["state"].unique())

state_data = data[data["state"] == state]

with col2:
    district = st.selectbox("Select District", state_data["district"].unique())

district_data = state_data[state_data["district"] == district]

with col3:
    taluk = st.selectbox("Select Taluk", district_data["taluk"].unique())

final_data = district_data[district_data["taluk"] == taluk]

# =============================
# TRAVEL INPUT
# =============================
st.subheader("🚗 Travel Details")

col4, col5, col6 = st.columns(3)

with col4:
    start = st.text_input("Starting Location")

with col5:
    end = st.text_input("Destination")

with col6:
    vehicle = st.selectbox("Vehicle", ["Car", "Bike", "Bus", "Auto"])

col7, col8 = st.columns(2)

with col7:
    mileage = st.number_input("Mileage (km/l)", 10, 50, 20)

with col8:
    fuel_price = st.number_input("Fuel Price ₹/liter", 80, 120, 100)

budget = st.slider("Select Budget ₹", 0, 5000, 2000)

# =============================
# DISTANCE (STATIC DEMO)
# =============================
distance = 120  # You can upgrade later with API

# =============================
# BUTTON ACTION
# =============================
if st.button("🚀 Plan My Trip"):

    # =============================
    # MAP ROUTE
    # =============================
    st.subheader("🗺 Route Map")
    map_link = f"https://www.google.com/maps/dir/{start}/{end}"
    st.markdown(f"[👉 Open Route in Google Maps]({map_link})")

    # =============================
    # TRAVEL COST
    # =============================
    st.subheader("💰 Travel Cost Calculation")

    fuel_needed = distance / mileage
    total_cost = fuel_needed * fuel_price

    st.success(f"Distance: {distance} km")
    st.success(f"Fuel Needed: {fuel_needed:.2f} liters")
    st.success(f"Estimated Cost: ₹{total_cost:.2f}")

    # =============================
    # FILTER DATA
    # =============================
    filtered = final_data[final_data["price"] <= budget]

    # =============================
    # SHOW PLACES
    # =============================
    st.subheader("📍 Tourist Places")
    places = filtered[filtered["type"] == "place"]

    if places.empty:
        st.warning("No places found")
    else:
        for _, row in places.iterrows():
            st.write(f"🔹 {row['place']} ⭐{row['rating']}")

    # =============================
    # SHOW HOTELS
    # =============================
    st.subheader("🏨 Hotels")
    hotels = filtered[filtered["type"] == "hotel"]

    if hotels.empty:
        st.warning("No hotels found")
    else:
        for _, row in hotels.iterrows():
            st.write(f"🔹 {row['place']} 💰₹{row['price']} ⭐{row['rating']}")

    # =============================
    # SHOW RESTAURANTS
    # =============================
    st.subheader("🍽 Restaurants")
    foods = filtered[filtered["type"] == "restaurant"]

    if foods.empty:
        st.warning("No restaurants found")
    else:
        for _, row in foods.iterrows():
            st.write(f"🔹 {row['place']} 💰₹{row['price']} ⭐{row['rating']}")

    # =============================
    # DAY PLAN
    # =============================
    st.subheader("🗓 Suggested Itinerary")

    all_places = filtered["place"].tolist()

    itinerary = []

    if len(all_places) == 0:
        st.warning("No itinerary available")
    else:
        for i in range(min(3, len(all_places))):
            plan = f"Day {i+1}: Visit {all_places[i]}"
            itinerary.append(plan)
            st.write(plan)

    # =============================
    # DOWNLOAD
    # =============================
    if itinerary:
        st.download_button(
            "📥 Download Itinerary",
            "\n".join(itinerary),
            file_name="travel_plan.txt"
        )