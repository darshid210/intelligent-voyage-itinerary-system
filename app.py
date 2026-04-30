import streamlit as st
import requests
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🌍 Intelligent Voyage Itinerary System")
st.markdown("### Real-Time Travel Planner (Like Google Maps)")

# =============================
# USER INPUT
# =============================
start = st.text_input("📍 Starting Location", "Tumakuru, Karnataka, India")
end = st.text_input("📍 Destination", "Davangere, Karnataka, India")

col1, col2, col3 = st.columns(3)

with col1:
    days = st.slider("📅 Number of Days", 1, 7, 3)

with col2:
    vehicle = st.selectbox("🚗 Vehicle", ["Car", "Bike", "Bus", "Auto"])

with col3:
    mileage = st.number_input("⛽ Mileage (km/l)", 10, 50, 20)

interest = st.selectbox("🎯 Interest", ["culture", "adventure", "food", "nature"])
fuel_price = st.number_input("💰 Fuel Price ₹/liter", 80, 120, 100)

# =============================
# FIXED GEOCODING FUNCTION
# =============================
def get_coords(place):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "json"}
        headers = {"User-Agent": "ivis-app"}

        res = requests.get(url, params=params, headers=headers).json()

        if res:
            return float(res[0]['lat']), float(res[0]['lon'])
        return None, None
    except:
        return None, None

# =============================
# SMART PLACE GENERATION
# =============================
def generate_places(interest):
    data = {
        "culture": ["Temple", "Fort", "Museum", "Palace"],
        "adventure": ["Hill", "Waterfall", "Trekking Spot"],
        "food": ["Restaurant", "Cafe", "Food Street"],
        "nature": ["Lake", "Park", "Forest"]
    }

    places = []
    for i in range(8):
        name = f"{interest.capitalize()} Place {i+1}"
        places.append({
            "name": name,
            "rating": round(4 + i*0.1, 1),
            "price": 100 + i*50
        })
    return places

# =============================
# MAIN BUTTON
# =============================
if st.button("🚀 Plan My Trip"):

    start_c = get_coords(start)
    end_c = get_coords(end)

    if start_c and end_c and start_c[0] and end_c[0]:

        # =============================
        # MAP
        # =============================
        st.subheader("🗺 Live Route Map")

        m = folium.Map(location=start_c, zoom_start=7)
        folium.Marker(start_c, tooltip="Start").add_to(m)
        folium.Marker(end_c, tooltip="End").add_to(m)

        folium.PolyLine([start_c, end_c], color="blue", weight=5).add_to(m)

        st_folium(m, width=900, height=500)

        # =============================
        # DISTANCE + COST
        # =============================
        distance = geodesic(start_c, end_c).km
        st.success(f"📏 Distance: {distance:.2f} km")

        fuel_needed = distance / mileage
        cost = fuel_needed * fuel_price

        st.success(f"⛽ Fuel Needed: {fuel_needed:.2f} liters")
        st.success(f"💰 Estimated Cost: ₹{cost:.2f}")

        # =============================
        # PLACES
        # =============================
        st.subheader("📍 Recommended Places")

        places = generate_places(interest)

        for p in places:
            st.write(f"🔹 {p['name']} ⭐{p['rating']} ₹{p['price']}")

        # =============================
        # HOTELS
        # =============================
        st.subheader("🏨 Hotels")

        for i in range(5):
            st.write(f"Hotel {i+1} ⭐{4+i*0.1} ₹{1500+i*300}")

        # =============================
        # RESTAURANTS
        # =============================
        st.subheader("🍽 Restaurants")

        for i in range(5):
            st.write(f"Restaurant {i+1} ⭐{4+i*0.1} ₹{300+i*100}")

        # =============================
        # ITINERARY
        # =============================
        st.subheader("🗓 Smart Itinerary")

        plan = []
        for i in range(days):
            p = places[i % len(places)]
            text = f"Day {i+1}: Visit {p['name']}"
            plan.append(text)
            st.write(text)

        st.download_button("📥 Download Plan", "\n".join(plan), "trip_plan.txt")

    else:
        st.error("❌ Could not find location. Try full name like 'Tumakuru, Karnataka, India'")