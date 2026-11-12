import streamlit as st
import requests
import pandas as pd
import altair as alt

# Central Israel coastline coordinates
LATITUDE = 32.08
LONGITUDE = 34.78

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")
st.title("🌊 Surf & Wind Forecast - Next 3 Days")

@st.cache_data
def get_forecast_data():
    # Fetch hourly wave height and period from Marine API
    marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=wave_height,wave_period&timezone=auto&forecast_days=3"
    wave_data = requests.get(marine_url).json()
    
    # Fetch hourly wind speed and direction from Weather API
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=wind_speed_10m,wind_direction_10m&timezone=auto&forecast_days=3"
    wind_data = requests.get(weather_url).json()
    
    # Combine arrays into a clean DataFrame
    df = pd.DataFrame({
        "Time": wave_data["hourly"]["time"],
        "Wave Height (m)": wave_data["hourly"]["wave_height"],
        "Period (s)": wave_data["hourly"]["wave_period"],
        "Wind Speed (km/h)": wind_data["hourly"]["wind_speed_10m"],
        "Wind Direction (°)": wind_data["hourly"]["wind_direction_10m"]
    })
    
    # Format date and time
    df["Time"] = pd.to_datetime(df["Time"]).dt.strftime("%d/%m %H:00")
    return df

def get_wind_type(direction):
    if pd.isna(direction):
        return ""
    if 45 <= direction <= 135:
        return "Offshore 💨"
    elif 225 <= direction <= 315:
        return "Onshore 🌊"
    else:
        return "Cross-shore"

# Load data and classify wind direction
df = get_forecast_data()
df["Wind Type"] = df["Wind Direction (°)"].apply(get_wind_type)

# Filter: Keep daylight hours only (06:00 to 18:00)
df_daylight = df[pd.to_datetime(df["Time"], format="%d/%m %H:%M").dt.hour.between(6, 18)]

# Find optimal surf windows
best_conditions = df_daylight[
    (df_daylight["Wave Height (m)"] >= 0.7) & 
    (df_daylight["Period (s)"] >= 6) & 
    (df_daylight["Wind Type"] == "Offshore 💨")
]

st.subheader("🏄 Session Recommendations")
if not best_conditions.empty:
    st.success("Classic conditions found! Offshore winds are grooming the swell and opening up the wall for pumping and rail carves. Best windows:")
    st.dataframe(best_conditions[["Time", "Wave Height (m)", "Period (s)", "Wind Speed (km/h)"]], hide_index=True)
elif df_daylight["Wave Height (m)"].max() < 0.5:
    st.warning("Looks flat over the next few days. Great time for a dry-land surfskate session to dial in your foot placement.")
else:
    st.info("No ideal offshore windows in the next few days, but check the table below for light-wind sessions.")

# Display static wave height chart locked to exact max peak
st.subheader("Wave Height Chart (24h)")
max_wave = float(df["Wave Height (m)"].max())
if pd.isna(max_wave) or max_wave <= 0:
    max_wave = 1.0

chart = (
    alt.Chart(df)
    .mark_line()
    .encode(
        x=alt.X("Time:N", sort=None, title="Time", axis=alt.Axis(labelOverlap=True, labelAngle=-45)),
        y=alt.Y(
            "Wave Height (m):Q",
            scale=alt.Scale(domain=[0, max_wave]),
            title="Wave Height (m)",
        ),
    )
    .properties(height=300)
)

st.altair_chart(chart, use_container_width=True)

# Display full daylight forecast table
st.subheader("Full Forecast (Daylight Hours)")
st.dataframe(df_daylight[["Time", "Wave Height (m)", "Period (s)", "Wind Type", "Wind Speed (km/h)"]], hide_index=True)
