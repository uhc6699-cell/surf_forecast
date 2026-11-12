import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Lock page width on mobile and allow horizontal scrolling ONLY inside the wave chart
st.markdown(
    """
    <style>
    html, body, .stApp {
        overflow-x: hidden !important;
        max-width: 100vw !important;
    }
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        overflow-y: hidden !important;
        -webkit-overflow-scrolling: touch;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Surf spots database: coordinates, coastline wind angles, and local cam URL
SPOTS = {
    "Herzliya (Marina / Dabush)": {
        "lat": 32.165,
        "lon": 34.792,
        "offshore": (55, 155),
        "onshore": (235, 335),
        "cam_url": "https://www.beachcam.co.il/herzliya.html",
    },
    "Tel Aviv - Hilton": {
        "lat": 32.090,
        "lon": 34.768,
        "offshore": (55, 155),
        "onshore": (235, 335),
        "cam_url": "https://www.beachcam.co.il/hilton.html",
    },
    "Tel Aviv - Dolphinarium": {
        "lat": 32.069,
        "lon": 34.760,
        "offshore": (55, 155),
        "onshore": (235, 335),
        "cam_url": "https://www.beachcam.co.il/dolphinarium.html",
    },
    "Ashdod - Gil Beach": {
        "lat": 31.812,
        "lon": 34.638,
        "offshore": (55, 155),
        "onshore": (235, 335),
        "cam_url": "https://www.beachcam.co.il/ashdod.html",
    },
    "Beit Yanai": {
        "lat": 32.378,
        "lon": 34.858,
        "offshore": (55, 155),
        "onshore": (235, 335),
        "cam_url": "https://www.beachcam.co.il/beityanai.html",
    },
    "Haifa - Bat Galim": {
        "lat": 32.836,
        "lon": 34.978,
        "offshore": (130, 225),
        "onshore": (310, 45),
        "cam_url": "https://www.beachcam.co.il/batgalim.html",
    },
}

st.title("🌊 Surf & Wind Forecast")

# 1. Spot Selector
selected_spot_name = st.selectbox("📍 Select Surf Spot", list(SPOTS.keys()))
spot = SPOTS[selected_spot_name]

# 2. Live Surf Cam Shortcut Buttons
cam_col1, cam_col2 = st.columns(2)
with cam_col1:
    st.link_button(f"📹 {selected_spot_name.split(' - ')[0]} Cam", spot["cam_url"], use_container_width=True)
with cam_col2:
    st.link_button("🎥 All Israel Cams (Beachcam)", "https://www.beachcam.co.il/", use_container_width=True)


@st.cache_data(ttl=1800)
def get_forecast_data(lat, lon):
    # Marine API: wave height, period, swell height, and sea surface temperature
    marine_url = (
        f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
        f"&hourly=wave_height,wave_period,swell_wave_height,sea_surface_temperature"
        f"&current=sea_surface_temperature&timezone=auto&forecast_days=3"
    )
    wave_data = requests.get(marine_url).json()

    # Weather API: wind speed, wind direction, and daily sunrise/sunset
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m"
        f"&daily=sunrise,sunset&timezone=auto&forecast_days=3"
    )
    wind_data = requests.get(weather_url).json()

    # Build hourly DataFrame
    df = pd.DataFrame({
        "DateTime": pd.to_datetime(wave_data["hourly"]["time"]),
        "Wave Height (m)": wave_data["hourly"]["wave_height"],
        "Swell (m)": wave_data["hourly"]["swell_wave_height"],
        "Period (s)": wave_data["hourly"]["wave_period"],
        "Wind Speed (km/h)": wind_data["hourly"]["wind_speed_10m"],
        "Wind Direction (°)": wind_data["hourly"]["wind_direction_10m"],
    })
    df["Date"] = df["DateTime"].dt.date
    df["Time"] = df["DateTime"].dt.strftime("%d/%m %H:00")

    # Build daily sunrise/sunset lookup table
    daily_df = pd.DataFrame({
        "Date": pd.to_datetime(wind_data["daily"]["time"]).date,
        "Sunrise": pd.to_datetime(wind_data["daily"]["sunrise"]),
        "Sunset": pd.to_datetime(wind_data["daily"]["sunset"]),
    })

    # Extract current water temperature safely
    water_temp = wave_data.get("current", {}).get("sea_surface_temperature")
    if water_temp is None:
        sst_series = pd.Series(wave_data["hourly"].get("sea_surface_temperature", [])).dropna()
        water_temp = float(sst_series.iloc[0]) if not sst_series.empty else None

    return df, daily_df, water_temp


def is_angle_in_range(angle, start, end):
    if start <= end:
        return start <= angle <= end
    return angle >= start or angle <= end


def get_wind_type(direction, offshore_range, onshore_range):
    if pd.isna(direction):
        return ""
    if is_angle_in_range(direction, *offshore_range):
        return "Offshore 💨"
    elif is_angle_in_range(direction, *onshore_range):
        return "Onshore 🌊"
    return "Cross-shore"


def get_wetsuit_recommendation(temp):
    if temp is None or pd.isna(temp):
        return "N/A", "Check local report"
    if temp >= 26.0:
        return f"{temp:.1f}°C", "Boardshorts / Lycra 🩳"
    elif temp >= 23.0:
        return f"{temp:.1f}°C", "Spring Suit / 2mm Top 👕"
    elif temp >= 20.0:
        return f"{temp:.1f}°C", "3/2mm Fullsuit 🩱"
    else:
        return f"{temp:.1f}°C", "4/3mm Fullsuit 🥶"


def calculate_surf_rating(row, offshore_range, onshore_range):
    h = row["Wave Height (m)"]
    p = row["Period (s)"]
    ws = row["Wind Speed (km/h)"]
    wd = row["Wind Direction (°)"]

    if pd.isna(h) or h < 0.35:
        return 1.0

    # 1. Wave height score (max 4.0 pts)
    if h < 0.5:
        height_score = 1.5
    elif h < 0.7:
        height_score = 2.4
    elif h < 1.0:
        height_score = 3.3
    elif h <= 2.2:
        height_score = 4.0
    else:
        height_score = 3.2  # Very large/stormy swell

    # 2. Wave period score (max 2.5 pts)
    if pd.isna(p) or p < 5.0:
        period_score = 0.5
    elif p < 6.5:
        period_score = 1.3
    elif p < 8.0:
        period_score = 2.0
    else:
        period_score = 2.5

    # 3. Wind quality score (max 3.5 pts)
    if pd.isna(wd) or pd.isna(ws):
        wind_score = 1.5
    elif is_angle_in_range(wd, *offshore_range):
        wind_score = 3.5 if ws <= 22 else 2.6
    elif ws < 8:
        wind_score = 3.1  # Glassy conditions
    elif is_angle_in_range(wd, *onshore_range):
        wind_score = 1.1 if ws <= 12 else 0.2
    else:
        wind_score = 2.0 if ws <= 15 else 1.1

    total = min(10.0, max(1.0, round(height_score + period_score + wind_score, 1)))
    return total


def format_rating_badge(score):
    if score >= 8.0:
        return f"{score}/10 🔥"
    elif score >= 6.5:
        return f"{score}/10 ✅"
    elif score >= 4.5:
        return f"{score}/10 👌"
    return f"{score}/10 💤"


# Load spot forecast
df, daily_df, water_temp = get_forecast_data(spot["lat"], spot["lon"])

# 3. Water Temperature, Wetsuit & Today's Sunrise/Sunset Cards
temp_display, wetsuit_advice = get_wetsuit_recommendation(water_temp)
today_sunrise = daily_df.iloc[0]["Sunrise"].strftime("%H:%M")
today_sunset = daily_df.iloc[0]["Sunset"].strftime("%H:%M")

m1, m2, m3 = st.columns(3)
m1.metric(label="🌡️ Water Temp", value=temp_display, delta=wetsuit_advice, delta_color="off")
m2.metric(label="🌅 Sunrise (Dawn)", value=today_sunrise)
m3.metric(label="🌇 Sunset (Dusk)", value=today_sunset)

# Classify wind and compute weighted surf rating
