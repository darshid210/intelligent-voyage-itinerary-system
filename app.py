import streamlit as st
import pandas as pd
import requests

# CONFIG
st.set_page_config(page_title="IVIS", layout="wide")

# LOAD DATA
data = pd.read_csv("data.csv")

# SIDEBAR (CHATBOT)
st.sidebar.title("🤖 Travel Assistant")

user_question = st.sidebar.text_input("Ask me anything")

def chatbot_reply(q):
    q = q.lower()

    if "budget" in q:
        return "Plan your trip by selecting places under your budget per day."
    elif "best place" in q:
        return "Manali and Goa are highly rated destinations."
    elif "weather" in q:
        return "You can check live weather in the main panel."
    elif "hello" in q:
        return "Hello! I am your travel assistant 😊"
    else:
        return "I can help with travel planning, budget, and destinations."

if user_question:
    st.sidebar.success(chatbot_reply(user_question))

# TITLE
st.title("🌍 Intelligent Voyage Itinerary System")

# INPUT UI
col1, col2, col3 = st.columns(3)

with col1:
    city = st.selectbox("Select City", data["city"].unique())

with col2:
    days = st.slider("Days", 1, 7, 3)

with col3:
    budget = st.number_input("Budget ₹", 1000, 50000, 10000)

# WEATHER API
API_KEY = "YOUR_API_KEY_HERE"

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        res = requests.get(url).json()
        return res["main"]["temp"], res["weather"][0]["description"]
    except:
        return None, None

# BUTTON
if st.button("Generate Smart Plan"):

    st.subheader("🌤 Weather")

    temp, desc = get_weather(city)

    if temp:
        st.info(f"{city}: {temp}°C, {desc}")
    else:
        st.warning("Weather not available")

    # SMART FILTER
    filtered = data[
        (data["city"] == city) &
        (data["price"] <= budget / days)
    ].sort_values(by=["rating", "price"], ascending=[False, True])

    st.subheader("📍 Top Recommendations")

    if filtered.empty:
        st.error("No places match your budget")
    else:
        for _, row in filtered.iterrows():
            st.markdown(f"""
            🔹 **{row['place']}**  
            ⭐ Rating: {row['rating']}  
            💰 Price: ₹{row['price']}  
            """)

    st.subheader("🗓️ Itinerary Plan")

    if not filtered.empty:
        places = filtered["place"].tolist()

        itinerary = []

        for i in range(days):
            place = places[i % len(places)]
            itinerary.append(f"Day {i+1}: Visit {place}")

            map_link = f"https://www.google.com/maps/search/{place}"
            st.write(f"Day {i+1}: {place}")
            st.markdown(f"[📍 View Map]({map_link})")

        # SAVE FEATURE
        st.download_button(
            label="📥 Download Itinerary",
            data="\n".join(itinerary),
            file_name="itinerary.txt"
        )