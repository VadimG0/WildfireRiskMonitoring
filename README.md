**Objective:** Develop a basic web-based dashboard that displays wildfire risk levels for user-specified locations using real-time weather data. This project simplifies the risk assessment to a display-only system without notifications or user accounts, making it achievable within a week.

* * * * *

### Key Features:

1.  **Weather Data Integration**:

    -   Use a weather API (e.g., OpenWeatherMap) to fetch real-time temperature, wind speed, and humidity for a given location.
    -   Simplify the wildfire risk calculation to a basic formula:
        -   High temperature + low humidity + high wind speed = High Risk
        -   Provide three risk levels: **Low**, **Medium**, and **High**.
2.  **Location Search**:

    -   Allow users to enter a city name or zip code to retrieve and display the wildfire risk level for that location.
3.  **Web-Based Interface**:

    -   A single-page web app with:
        -   Input field for the location.
        -   Display of current weather data (temperature, humidity, wind speed).
        -   Display of the wildfire risk level based on simple thresholds.
4.  **Static Risk Guide**:

    -   Include a guide explaining the risk levels and what they mean (e.g., "High Risk: Conditions are favorable for wildfires to spread quickly.").

* * * * *

### Steps to Implement:

1.  **Set Up API Integration**:

    -   Obtain an API key from OpenWeatherMap or similar service.
    -   Write a function to fetch weather data based on user input.
2.  **Wildfire Risk Calculation**:

    -   Define simple thresholds for Low, Medium, and High risk.
        -   Example:
            -   Low: Temperature < 75°F, Humidity > 40%, Wind Speed < 10 mph
            -   Medium: Temperature 75--90°F, Humidity 20--40%, Wind Speed 10--20 mph
            -   High: Temperature > 90°F, Humidity < 20%, Wind Speed > 20 mph
3.  **Build the Frontend**:

    -   Use basic HTML, CSS, and JavaScript (or a lightweight framework like **Flask** for Python or **React** for a dynamic experience).
    -   Add a simple form for users to input location data.
4.  **Display Results**:

    -   Show weather data (e.g., temperature, humidity, wind speed) and the calculated wildfire risk level.
5.  **Static Risk Guide**:

    -   Add a small section explaining risk levels and associated precautions.
