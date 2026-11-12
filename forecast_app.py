import json
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Exact Clone CSS from the screenshot
st.markdown(
    """
    <style>
    /* Background exactly like the mockup */
    .stApp, .stApp > header {
        background-color: #F2EEE5 !important;
    }
    .block-container {
        padding: 0.5rem 1rem 80px 1rem !important;
    }
    
    /* Hide Streamlit default UI elements */
    header[data-testid="stHeader"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Prevent horizontal page overflow on mobile */
    .stApp { overflow-x: clip !important; }
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    
    /* Typography */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1A2B4C;
    }
    
    /* Custom Header */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }
    .hamburger {
        font-size: 24px;
        color: #555;
        cursor: pointer;
    }
    .title-container {
        text-align: center;
        flex-grow: 1;
    }
    .main-title {
        font-size: 1.3rem;
        font-weight: 800;
        color: #1A2B4C;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    /* Native selectbox override to act as subtitle */
    div[data-testid="stSelectbox"] {
        margin-top: -15px;
        margin-bottom: 10px;
    }
    div[data-testid="stSelectbox"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stSelectbox"] * {
        color: #4B5563 !important;
        text-align: center !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    
    /* Cam Buttons */
    .cam-buttons {
        display: flex;
        gap: 12px;
        margin-bottom: 16px;
    }
    .cam-btn-dark {
        flex: 1;
        background-color: #1A2B4C;
        color: #FFFFFF !important;
        padding: 12px 10px;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .cam-btn-light {
        flex: 1;
        background-color: transparent;
        border: 1px solid #1A2B4C;
        color: #1A2B4C !important;
        padding: 12px 10px;
        border-radius: 8px;
        text-align: center;
        text-decoration: none;
        font-size: 0.85rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    
    /* Unified Stats Card */
    .unified-stat-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 18px 10px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .stat-col {
        text-align: center;
        flex: 1;
    }
    .stat-main {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .stat-sub {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6B7280 !important;
    }
    
    /* Daily Forecast List */
    .forecast-card {
        background: #FFFFFF;
        border-radius: 16px;
        padding: 16px 20px;
        margin-top: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .forecast-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #1A2B4C;
    }
    .f-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .f-row:last-child { border-bottom: none; }
    .f-day { font-weight: 700; font-size: 0.95rem; width: 45px; }
    .f-dots { display: flex; gap: 6px; }
    .f-dot { width: 12px; height: 12px; border-radius: 50%; }
    .f-score { font-size: 0.85rem; font-weight: 600; text-align: right; min-width: 90px; color: #4B5563;}
    
    /* Bottom Nav */
    .bottom-nav {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        height: 75px;
        background: #FFFFFF;
        border-top: 1px solid #E5E7EB;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 9999;
        padding-bottom: env(safe-area-inset-bottom);
    }
    .nav-icon { font-size: 24px; color: #9CA3AF; }
    .nav-icon.active { color: #1A2B4C; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Top Custom Header
st.markdown(
    """
    <div class="custom-header">
        <div class="hamburger">≡</div>
        <div class="title-container">
            <div class="main-title">🌊 Surf & Wind</div>
        </div>
        <div style="width: 24px;"></div>
    </div>
    """,
    unsafe_allow_html=True
)

SPOTS = {
    "Herzliya (Marina / Dabush)": {"lat": 32.165, "lon": 34.792, "offshore": (55, 155), "onshore": (235, 335), "cam": "https://www.beachcam.co.il/herzliya.html"},
    "Tel Aviv - Hilton": {"lat": 32.090, "lon": 34.768, "offshore": (55, 155), "onshore": (235, 335), "cam": "https://www.beachcam.co.il/hilton.html"},
    "Tel Aviv - Dolphinarium": {"lat": 32.069, "lon": 34.760, "offshore": (55, 155), "onshore": (235, 335), "cam": "https://www.beachcam.co.il/dolphinarium.html"},
    "Ashdod - Gil Beach": {"lat": 31.812, "lon": 34.638, "offshore": (55, 155), "onshore": (235, 335), "cam": "https://www.beachcam.co.il/ashdod.html"},
    "Beit Yanai": {"lat": 32.378, "lon": 34.858, "offshore": (55, 155), "onshore": (235, 335), "cam": "https://www.beachcam.co.il/beityanai.html"},
    "Haifa - Bat Galim": {"lat": 32.836, "lon": 34.978, "offshore": (130, 225), "onshore": (310, 45), "cam": "https://www.beachcam.co.il/batgalim.html"},
}

selected_spot_name = st.selectbox("", list(SPOTS.keys()), label_visibility="collapsed")
spot = SPOTS[selected_spot_name]
short_spot_name = selected_spot_name.split(" (")[0].split(" - ")[-1]

# Cams
st.markdown(
    f"""
    <div class="cam-buttons">
        <a class="cam-btn-dark" href="{spot['cam']}" target="_blank">📹 {short_spot_name} Cam</a>
        <a class="cam-btn-light" href="https://www.beachcam.co.il/" target="_blank">📹 All Israel Cams</a>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data(ttl=1800)
def get_forecast_data(lat, lon):
    marine_url = (
        f"https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}"
        f"&hourly=wave_height,wave_period,swell_wave_height,sea_surface_temperature"
        f"&current=sea_surface_temperature&timezone=auto&forecast_days=7"
    )
    wave_data = requests.get(marine_url).json()

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m"
        f"&timezone=auto&forecast_days=7"
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
    df["Day"] = df["DateTime"].dt.strftime("%a")
    df["HourStr"] = df["DateTime"].dt.strftime("%H:00")
    df["Time"] = df["DateTime"].dt.strftime("%a %H:00")

    water_temp = wave_data.get("current", {}).get("sea_surface_temperature")
    if water_temp is None:
        sst_series = pd.Series(wave_data["hourly"].get("sea_surface_temperature", [])).dropna()
        water_temp = float(sst_series.iloc[0]) if not sst_series.empty else None

    return df, water_temp

def get_wetsuit_icon_text(temp):
    if temp is None or pd.isna(temp): return "❓", "N/A"
    if temp >= 26.0: return "🩳", "Boardshorts"
    if temp >= 23.0: return "🩱", "Spring / 2mm"
    if temp >= 20.0: return "👕", "3/2mm Suit"
    return "🥶", "4/3mm Suit"

def is_angle_in_range(angle, start, end):
    if start <= end: return start <= angle <= end
    return angle >= start or angle <= end

def calculate_surf_rating(row, offshore_range, onshore_range):
    h, p = row["Wave Height (m)"], row["Period (s)"]
    ws, wd = row["Wind Speed (km/h)"], row["Wind Direction (°)"]

    if pd.isna(h) or h < 0.2: return 1.0
    if h < 0.6: return round(min(4.9, 1.0 + (h / 0.6) * 3.5), 1)

    height_score = 2.4 if h < 0.7 else (3.3 if h < 1.0 else (4.0 if h <= 2.2 else 3.2))
    period_score = 0.5 if pd.isna(p) or p < 5.0 else (1.3 if p < 6.5 else (2.0 if p < 8.0 else 2.5))
    
    if pd.isna(wd) or pd.isna(ws): wind_score = 1.5
    elif is_angle_in_range(wd, *offshore_range): wind_score = 3.5 if ws <= 22 else 2.6
    elif ws < 8: wind_score = 3.1
    elif is_angle_in_range(wd, *onshore_range): wind_score = 1.1 if ws <= 12 else 0.2
    else: wind_score = 2.0 if ws <= 15 else 1.1

    return min(10.0, max(5.0, round(height_score + period_score + wind_score, 1)))

def get_rating_hex(score):
    if score >= 7.0: return "#48BB78" # Green
    elif score >= 4.0: return "#ECC94B" # Yellow/Orange
    return "#F56565" # Red

df, water_temp = get_forecast_data(spot["lat"], spot["lon"])
unique_dates = sorted(df["Date"].unique())
df["DayIdx"] = df["Date"].map({d: i for i, d in enumerate(unique_dates)})
df["Score"] = df.apply(lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1)

# Stats Card
temp_str = f"{water_temp:.1f}°C" if water_temp else "N/A"
suit_icon, suit_text = get_wetsuit_icon_text(water_temp)

st.markdown(
    f"""
    <div class="unified-stat-card">
        <div class="stat-col">
            <div class="stat-main">🌡️ {temp_str}</div>
            <div class="stat-sub">טמפרטורת מים</div>
        </div>
        <div class="stat-col">
            <div class="stat-main">{suit_icon}</div>
            <div class="stat-sub">{suit_text}</div>
        </div>
        <div class="stat-col">
            <div class="stat-main">🌅🌇</div>
            <div class="stat-sub">Sunrise & Sunset</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Smooth Wave Chart
df_chart = df[df["DateTime"].dt.hour.between(6, 17)].copy()
max_wave_m = float(df_chart["Wave Height (m)"].max())
if pd.isna(max_wave_m) or max_wave_m <= 0: max_wave_m = 1.0
max_wave_cm = int(round(max_wave_m * 100))

points_data = []
for _, row in df_chart.iterrows():
    val = row["Wave Height (m)"]
    points_data.append({
        "day": row["Day"],
        "dayIdx": int(row["DayIdx"]),
        "hour": int(row["DateTime"].hour),
        "waveRaw": 0.0 if pd.isna(val) else float(val),
    })

html_chart = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {{ box-sizing: border-box; user-select: none; }}
  body {{ margin: 0; font-family: -apple-system, sans-serif; background: transparent; }}
  .chart-card {{ background: #FFFFFF; border-radius: 16px; padding: 16px 12px 10px 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }}
  .c-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; padding: 0 4px; }}
  .c-title {{ font-size: 1.05rem; font-weight: 700; color: #1A2B4C; }}
  .c-max {{ font-size: 0.9rem; font-weight: 700; color: #1A2B4C; }}
  .chart-shell {{ width: 100%; height: 160px; position: relative; overflow-x: auto; overflow-y: hidden; }}
</style>
</head>
<body oncontextmenu="return false;">
  <div class="chart-card">
    <div class="c-header">
      <div class="c-title">Wave Height</div>
      <div class="c-max">Max: {max_wave_cm}cm</div>
    </div>
    <div class="chart-shell" id="scrollArea">
      <svg id="waveSvg" height="160"></svg>
    </div>
  </div>
  <script>
    const points = {json.dumps(points_data)};
    const maxWave = {max_wave_m};
    const stepX = 24, padLeft = 10, padRight = 20, padTop = 15, padBottom = 30;
    const plotHeight = 160 - padTop - padBottom;
    const svgWidth = Math.max(350, padLeft + padRight + (points.length - 1) * stepX);
    const svg = document.getElementById("waveSvg");
    svg.setAttribute("width", svgWidth);
    
    const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `<linearGradient id="waveGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#8997A8"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0.2"/>
    </linearGradient>`;
    svg.appendChild(defs);
    
    function createSvg(tag, attrs) {{
      const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
      return el;
    }}
    
    const coords = points.map((p, i) => ({{ ...p, x: padLeft + i * stepX, y: padTop + plotHeight * (1 - Math.min(1, Math.max(0, p.waveRaw / maxWave))) }}));
    
    // Smooth Bezier Curve
    let pathD = "";
    coords.forEach((c, idx) => {{
        if (idx === 0) pathD += `M ${{c.x}} ${{c.y}}`;
        else {{
            const prev = coords[idx - 1];
            const cpX = (prev.x + c.x) / 2;
            pathD += ` C ${{cpX}} ${{prev.y}}, ${{cpX}} ${{c.y}}, ${{c.x}} ${{c.y}}`;
        }}
    }});
    
    const fillD = pathD + ` L ${{coords[coords.length-1].x}} ${{padTop + plotHeight}} L ${{coords[0].x}} ${{padTop + plotHeight}} Z`;
    svg.appendChild(createSvg("path", {{ d: fillD, fill: "url(#waveGrad)" }}));
    svg.appendChild(createSvg("path", {{ d: pathD, fill: "none", stroke: "#2C3E50", "stroke-width": "3", "stroke-linecap": "round" }}));
    
    // Draw Day Labels at roughly midday
    coords.forEach(c => {{
      if (c.hour === 12) {{
        const label = createSvg("text", {{ x: c.x, y: padTop + plotHeight + 20, fill: "#4B5563", "font-size": "11", "font-weight": "600", "text-anchor": "middle" }});
        label.textContent = c.day;
        svg.appendChild(label);
      }}
    }});
  </script>
</body>
</html>
"""
components.html(html_chart, height=225)

# Daily Forecast List with 4 colored dots per day
st.markdown('<div class="forecast-card"><div class="forecast-title">Daily Forecast</div>', unsafe_allow_html=True)

list_html = ""
for d in unique_dates:
    day_df = df[df["Date"] == d]
    if day_df.empty: continue
    
    # 4 periods for 4 dots: Morning(6-8), Late Morning(9-11), Noon(12-14), Afternoon(15-17)
    periods = [(6, 8), (9, 11), (12, 14), (15, 17)]
    dot_colors = []
    for s_hr, e_hr in periods:
        sub = day_df[day_df["DateTime"].dt.hour.between(s_hr, e_hr)]
        if sub.empty: dot_colors.append("#E5E7EB")
        else: dot_colors.append(get_rating_hex(sub["Score"].max()))
    
    # Best session
    dl_df = day_df[day_df["DateTime"].dt.hour.between(6, 17)]
    if dl_df.empty: dl_df = day_df
    best_row = dl_df.loc[dl_df["Score"].idxmax()]
    
    day_name = pd.Timestamp(d).strftime("%a")
    if pd.Timestamp(d).date() == datetime.now().date(): day_name = "Today"
    
    list_html += f"""
    <div class="f-row">
        <div class="f-day">{day_name}</div>
        <div class="f-dots">
            <div class="f-dot" style="background:{dot_colors[0]};"></div>
            <div class="f-dot" style="background:{dot_colors[1]};"></div>
            <div class="f-dot" style="background:{dot_colors[2]};"></div>
            <div class="f-dot" style="background:{dot_colors[3]};"></div>
        </div>
        <div class="f-score">{best_row['HourStr']} ({best_row['Score']}/10)</div>
    </div>
    """

st.markdown(list_html + '</div>', unsafe_allow_html=True)

# Bottom Nav Bar (Visual only, to match mockup completely)
st.markdown(
    """
    <div class="bottom-nav">
        <div class="nav-icon active">🏠</div>
        <div class="nav-icon">🧭</div>
        <div class="nav-icon">🔔</div>
        <div class="nav-icon">⚙️</div>
    </div>
    """,
    unsafe_allow_html=True
)
