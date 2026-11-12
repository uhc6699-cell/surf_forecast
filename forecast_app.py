import streamlit as st
import requests
import pandas as pd
import altair as alt

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Prevent horizontal page overflow without locking vertical touch scrolling on mobile
st.markdown(
    """
    <style>
    .stApp {
        overflow-x: clip !important;
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
    .compact-row {
        display: flex;
        gap: 8px;
        width: 100%;
        margin-bottom: 10px;
    }
    .cam-btn {
        flex: 1;
        text-align: center;
        padding: 9px 6px;
        border-radius: 8px;
        background-color: var(--secondary-background-color);
        color: var(--text-color) !important;
        text-decoration: none !important;
        border: 1px solid rgba(128, 128, 128, 0.3);
        font-size: 0.85rem;
        font-weight: 600;
    }
    .stat-card {
        flex: 1;
        padding: 8px 6px;
        border-radius: 10px;
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.25);
        text-align: center;
    }
    .stat-label {
        font-size: 0.72rem;
        opacity: 0.8;
        margin-bottom: 2px;
    }
    .stat-value {
        font-size: 1.15rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .stat-sub {
        font-size: 0.7rem;
        margin-top: 3px;
        opacity: 0.9;
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

st.subheader("🌊 Surf & Wind Forecast")

# 1. Spot Selector
selected_spot_name = st.selectbox("📍 Select Surf Spot", list(SPOTS.keys()))
spot = SPOTS[selected_spot_name]
short_spot_name = selected_spot_name.split(" (")[0].split(" - ")[-1]

# 2. Side-by-side Live Cam Buttons (compact on mobile)
st.markdown(
    f"""
    <div class="compact-row">
        <a class="cam-btn" href="{spot['cam_url']}" target="_blank">📹 {short_spot_name} Cam</a>
        <a class="cam-btn" href="https://www.beachcam.co.il/" target="_blank">🎥 All Israel Cams</a>
    </div>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=1800)
def get_forecast_data(lat, lon):
    marine_url = (
        f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
        f"&hourly=wave_height,wave_period,swell_wave_height,sea_surface_temperature"
        f"&current=sea_surface_temperature&timezone=auto&forecast_days=3"
    )
    wave_data = requests.get(marine_url).json()

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m"
        f"&daily=sunrise,sunset&timezone=auto&forecast_days=3"
    )
    wind_data = requests.get(weather_url).json()

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

    daily_df = pd.DataFrame({
        "Date": pd.to_datetime(wind_data["daily"]["time"]).date,
        "Sunrise": pd.to_datetime(wind_data["daily"]["sunrise"]),
        "Sunset": pd.to_datetime(wind_data["daily"]["sunset"]),
    })

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
        return "N/A", "Check report"
    if temp >= 26.0:
        return f"{temp:.1f}°C", "Boardshorts 🩳"
    elif temp >= 23.0:
        return f"{temp:.1f}°C", "Spring / 2mm 👕"
    elif temp >= 20.0:
        return f"{temp:.1f}°C", "3/2mm Suit 🩱"
    else:
        return f"{temp:.1f}°C", "4/3mm Suit 🥶"


def calculate_surf_rating(row, offshore_range, onshore_range):
    h = row["Wave Height (m)"]
    p = row["Period (s)"]
    ws = row["Wind Speed (km/h)"]
    wd = row["Wind Direction (°)"]

    if pd.isna(h) or h < 0.35:
        return 1.0

    if h < 0.5:
        height_score = 1.5
    elif h < 0.7:
        height_score = 2.4
    elif h < 1.0:
        height_score = 3.3
    elif h <= 2.2:
        height_score = 4.0
    else:
        height_score = 3.2

    if pd.isna(p) or p < 5.0:
        period_score = 0.5
    elif p < 6.5:
        period_score = 1.3
    elif p < 8.0:
        period_score = 2.0
    else:
        period_score = 2.5

    if pd.isna(wd) or pd.isna(ws):
        wind_score = 1.5
    elif is_angle_in_range(wd, *offshore_range):
        wind_score = 3.5 if ws <= 22 else 2.6
    elif ws < 8:
        wind_score = 3.1
    elif is_angle_in_range(wd, *onshore_range):
        wind_score = 1.1 if ws <= 12 else 0.2
    else:
        wind_score = 2.0 if ws <= 15 else 1.1

    return min(10.0, max(1.0, round(height_score + period_score + wind_score, 1)))


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

# 3. Side-by-side Water Temp, Sunrise & Sunset Cards (compact on mobile)
temp_display, wetsuit_advice = get_wetsuit_recommendation(water_temp)
today_sunrise = daily_df.iloc[0]["Sunrise"].strftime("%H:%M")
today_sunset = daily_df.iloc[0]["Sunset"].strftime("%H:%M")

st.markdown(
    f"""
    <div class="compact-row">
        <div class="stat-card">
            <div class="stat-label">🌡️ Water</div>
            <div class="stat-value">{temp_display}</div>
            <div class="stat-sub">{wetsuit_advice}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">🌅 Sunrise</div>
            <div class="stat-value">{today_sunrise}</div>
            <div class="stat-sub">Dawn Patrol</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">🌇 Sunset</div>
            <div class="stat-value">{today_sunset}</div>
            <div class="stat-sub">Last Light</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Classify wind and compute weighted surf rating
df["Wind Type"] = df["Wind Direction (°)"].apply(
    lambda d: get_wind_type(d, spot["offshore"], spot["onshore"])
)
df["Score"] = df.apply(
    lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1
)
df["Rating"] = df["Score"].apply(format_rating_badge)

# 4. Dynamic Daylight Filter
df = df.merge(daily_df, on="Date", how="left")
df_daylight = df[
    (df["DateTime"] >= (df["Sunrise"] - pd.Timedelta(minutes=30)))
    & (df["DateTime"] <= (df["Sunset"] + pd.Timedelta(minutes=30)))
].copy()

# 5. Session Recommendations
best_conditions = df_daylight[df_daylight["Score"] >= 6.8]

st.subheader("🏄 Session Recommendations")
if not best_conditions.empty:
    st.success(
        f"Prime windows spotted at {selected_spot_name}! Clean wall and favorable winds for pumping and rail carves:"
    )
    st.dataframe(
        best_conditions[["Time", "Rating", "Wave Height (m)", "Period (s)", "Wind Type", "Wind Speed (km/h)"]],
        hide_index=True,
    )
elif df_daylight["Wave Height (m)"].max() < 0.45:
    st.warning("Flat spell ahead. Ideal time for a dry-land surfskate session to dial in foot placement and carving mechanics.")
else:
    st.info("No high-scoring sessions yet, check the highest-rated daylight hours in the table below.")

# 6. Horizontally scrollable wave height chart locked to max peak
st.subheader("Wave Height Chart (Swipe chart horizontally →)")
max_wave = float(df["Wave Height (m)"].max())
if pd.isna(max_wave) or max_wave <= 0:
    max_wave = 1.0

chart = (
    alt.Chart(df)
    .mark_line(point=alt.OverlayMarkDef(size=45))
    .encode(
        x=alt.X(
            "DateTime:T",
            title="Time",
            axis=alt.Axis(format="%d/%m %H:%M", labelAngle=-45, tickCount=24),
        ),
        y=alt.Y(
            "Wave Height (m):Q",
            scale=alt.Scale(domain=[0, max_wave]),
            title="Wave Height (m)",
        ),
        tooltip=["Time", "Rating", "Wave Height (m)", "Swell (m)", "Period (s)", "Wind Type", "Wind Speed (km/h)"],
    )
    .properties(width=1400, height=300)
)

st.altair_chart(chart, use_container_width=False)

# 7. Full Daylight Forecast Table
st.subheader("Full Daylight Forecast (Dawn to Dusk)")
st.dataframe(
    df_daylight[["Time", "Rating", "Wave Height (m)", "Swell (m)", "Period (s)", "Wind Type", "Wind Speed (km/h)"]],
    hide_index=True,
)
