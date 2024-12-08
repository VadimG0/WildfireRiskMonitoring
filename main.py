import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go
import random

# Set the directory where the dataset is located
current_dir = Path(__file__).parent.resolve()
DATA_FILE = current_dir / "data" / "daily_weather_data.csv"

@st.cache_data
def load_dataset():
    try:
        data = pd.read_csv(DATA_FILE)
        # Clean column names to be lowercase and stripped of spaces
        data.columns = data.columns.str.strip().str.lower()
        return data
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return None

# Function to calculate wildfire risk
def calculate_risk(temp, wind_speed):
    if temp > 30 and wind_speed > 20:
        return "High"
    elif temp > 25 and wind_speed > 10:
        return "Medium"
    else:
        return "Low"

# Function to generate a 7-day forecast
def generate_forecast(current_temp, current_wind_speed):
    forecast = []
    for day in range(7):
        temp = current_temp + random.uniform(-2, 2)  # Random fluctuation of ±2°C
        wind_speed = current_wind_speed + random.uniform(-5, 5)  # Random fluctuation of ±5 km/h
        risk = calculate_risk(temp, wind_speed)
        forecast.append({"day": f"Day {day + 1}", "temp": temp, "wind_speed": wind_speed, "risk": risk})
    return forecast

# Function to create map with wildfire risk level
def create_map(lat, lon, city, risk_level):
    risk_colors = {"Low": "green", "Medium": "orange", "High": "red"}
    color = risk_colors.get(risk_level, "gray")

    # Create map centered on the location
    wildfire_map = folium.Map(location=[lat, lon], zoom_start=6)

    # Add a marker for the location
    folium.Marker(
        location=[lat, lon],
        popup=f"<b>{city}</b><br>Risk Level: {risk_level}",
        icon=folium.Icon(color=color),
    ).add_to(wildfire_map)

    return wildfire_map

# Main Streamlit application
def main():
    st.title("Wildfire Risk Dashboard")
    st.markdown("""
    This dashboard helps assess wildfire risk levels based on the uploaded dataset.
    Enter a city to view the wildfire risk for that area and a 7-day forecast.
    """)

    # Load dataset
    data = load_dataset()
    if data is None:
        return

    st.write("Dataset loaded successfully!")
    st.dataframe(data.head())

    # Verify the required columns
    required_columns = {"city", "latitude", "longitude", "tavg", "wspd"}
    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        st.error(f"The dataset is missing required columns: {', '.join(missing_columns)}")
        return

    # User input for city
    city = st.text_input("Enter a city (e.g., 'New York'):", "").strip().lower()

    if city:
        st.write(f"Fetching weather data for: **{city}**")

        # Filter data by city
        city_data = data[data["city"].str.lower() == city]
        if city_data.empty:
            st.error("City not found in dataset.")
            return

        # Extract relevant data
        temp = city_data["tavg"].iloc[0]
        wind_speed = city_data["wspd"].iloc[0]
        lat = city_data["latitude"].iloc[0]
        lon = city_data["longitude"].iloc[0]

        # Calculate wildfire risk
        risk_level = calculate_risk(temp, wind_speed)

        # Display weather data
        st.subheader("Current Weather Data")
        st.write(f"**Average Temperature:** {temp:.1f} °C")
        st.write(f"**Wind Speed:** {wind_speed:.1f} km/h")

        # Display risk level
        st.subheader("Wildfire Risk Level")
        st.write(f"The wildfire risk level for **{city}** is: **{risk_level}**")

        # Create and display map with wildfire risk
        st.subheader("Map Visualization")
        wildfire_map = create_map(lat, lon, city, risk_level)
        st_folium(wildfire_map, width=700, height=500)

        # Historical trends
        if st.button("Show Historical Trends"):
            historical_data = city_data.tail(7)  # Last 7 days
            temps = historical_data["tavg"]
            wind_speeds = historical_data["wspd"]

            fig = go.Figure()
            fig.add_trace(go.Scatter(y=temps, mode='lines', name='Average Temperature (°C)'))
            fig.add_trace(go.Scatter(y=wind_speeds, mode='lines', name='Wind Speed (km/h)'))
            st.plotly_chart(fig)

        # 7-day forecast
        if st.button("Show 7-Day Forecast"):
            forecast = generate_forecast(temp, wind_speed)
            st.subheader("7-Day Wildfire Risk Forecast")
            for day_forecast in forecast:
                st.write(
                    f"{day_forecast['day']}: "
                    f"**Temperature:** {day_forecast['temp']:.1f} °C, "
                    f"**Wind Speed:** {day_forecast['wind_speed']:.1f} km/h, "
                    f"**Risk Level:** {day_forecast['risk']}"
                )

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
        main()
    else:
        script_path = os.path.abspath(__file__)
        os.system(f"streamlit run {script_path} streamlit")
        sys.exit()
