import os
import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import folium
from streamlit_folium import st_folium
import plotly.graph_objects as go

# Set the directory where the dataset is located
current_dir = Path(__file__).parent.resolve()
DATA_FILE = current_dir / "data" / "daily_weather_data.csv"

@st.cache_data
def load_dataset():
    try:
        data = pd.read_csv(DATA_FILE)
        # Clean column names to be lowercase and stripped of spaces
        data.columns = data.columns.str.strip().str.lower()
        data['date'] = pd.to_datetime(data['date'])  # Ensure date column is datetime
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

# Function to train a machine learning model
def train_model(city_data):
    # Feature Engineering
    city_data = city_data.sort_values('date')  # Ensure data is sorted by date
    city_data['day_of_year'] = city_data['date'].dt.dayofyear

    # Lagged Features for Prediction
    for lag in range(1, 8):
        city_data[f'tavg_lag_{lag}'] = city_data['tavg'].shift(lag)
        city_data[f'wspd_lag_{lag}'] = city_data['wspd'].shift(lag)

    city_data = city_data.dropna()  # Drop rows with missing values after lagging

    # Features and Targets
    features = [col for col in city_data.columns if 'lag' in col or col == 'day_of_year']
    target_temp = 'tavg'
    target_wind = 'wspd'

    X = city_data[features]
    y_temp = city_data[target_temp]
    y_wind = city_data[target_wind]

    # Split Data
    X_train, X_test, y_temp_train, y_temp_test = train_test_split(X, y_temp, test_size=0.2, random_state=42)
    _, _, y_wind_train, y_wind_test = train_test_split(X, y_wind, test_size=0.2, random_state=42)

    # Train Models
    temp_model = RandomForestRegressor(random_state=42)
    wind_model = RandomForestRegressor(random_state=42)

    temp_model.fit(X_train, y_temp_train)
    wind_model.fit(X_train, y_wind_train)

    return (temp_model, wind_model), features, city_data

# Function to predict the next 7 days
def predict_next_7_days(models, features, recent_data):
    temp_model, wind_model = models

    # Prepare data for prediction
    future_data = []
    for day in range(7):  # Iterate for the next 7 days
        # Use the most recent data and append predictions iteratively
        if future_data:
            last_row = future_data[-1]
        else:
            last_row = recent_data.iloc[-1].to_dict()  # Convert last row to dictionary

        day_of_year = (last_row['day_of_year'] + 1) % 365

        # Generate lagged features for temperature and wind speed
        new_row = {}
        for lag in range(1, 8):
            new_row[f'tavg_lag_{lag}'] = last_row[f'tavg_lag_{lag - 1}'] if lag > 1 else last_row['tavg']
            new_row[f'wspd_lag_{lag}'] = last_row[f'wspd_lag_{lag - 1}'] if lag > 1 else last_row['wspd']

        # Add the day of the year
        new_row['day_of_year'] = day_of_year

        # Convert to DataFrame for prediction
        input_df = pd.DataFrame([new_row])

        # Predict temperature and wind speed
        predicted_temp = temp_model.predict(input_df[features])[0]
        predicted_wind = wind_model.predict(input_df[features])[0]

        # Append predictions to future_data
        new_row['tavg'] = predicted_temp
        new_row['wspd'] = predicted_wind
        future_data.append(new_row)

    # Return predictions as a DataFrame
    return pd.DataFrame(future_data)

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
    required_columns = {"city", "latitude", "longitude", "tavg", "wspd", "date"}
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
        temp = city_data["tavg"].iloc[-1]
        wind_speed = city_data["wspd"].iloc[-1]
        lat = city_data["latitude"].iloc[0]
        lon = city_data["longitude"].iloc[0]

        # Calculate wildfire risk
        risk_level = calculate_risk(temp, wind_speed)

        # Display map
        st.subheader("Location and Wildfire Risk Map")
        wildfire_map = create_map(lat, lon, city, risk_level)
        st_folium(wildfire_map, width=700, height=500)

        # Display historical trends
        st.subheader("Historical Trends")
        historical_data = city_data.tail(30)  # Last 30 days
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['tavg'], mode='lines', name='Temperature (°C)'))
        fig.add_trace(go.Scatter(x=historical_data['date'], y=historical_data['wspd'], mode='lines', name='Wind Speed (km/h)'))
        fig.update_layout(title="Historical Weather Trends", xaxis_title="Date", yaxis_title="Value", template="plotly_white")
        st.plotly_chart(fig)

        # Train machine learning models
        models, features, processed_data = train_model(city_data)

        # Use processed data for recent_data
        recent_data = processed_data.tail(7)

        # Generate 7-day forecast
        forecast = predict_next_7_days(models, features, recent_data)

        # Display forecast
        st.subheader("7-Day Wildfire Risk Forecast")
        for idx, row in forecast.iterrows():
            risk_level = calculate_risk(row['tavg'], row['wspd'])
            st.write(
                f"Day {idx + 1}: "
                f"**Temperature:** {row['tavg']:.1f} °C, "
                f"**Wind Speed:** {row['wspd']:.1f} km/h, "
                f"**Risk Level:** {risk_level}"
            )

        # Visualize forecast
        st.subheader("Forecast Visualization")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[f"Day {i + 1}" for i in range(7)],
            y=forecast['tavg'],
            mode='lines+markers',
            name='Temperature (°C)'
        ))
        fig.add_trace(go.Scatter(
            x=[f"Day {i + 1}" for i in range(7)],
            y=forecast['wspd'],
            mode='lines+markers',
            name='Wind Speed (km/h)'
        ))
        fig.update_layout(
            title="7-Day Forecast for Temperature and Wind Speed",
            xaxis_title="Day",
            yaxis_title="Value",
            legend_title="Metrics",
            template="plotly_white"
        )
        st.plotly_chart(fig)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "streamlit":
        main()
    else:
        script_path = os.path.abspath(__file__)
        os.system(f"streamlit run {script_path} streamlit")
        sys.exit()
