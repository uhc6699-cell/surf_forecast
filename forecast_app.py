import json
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Minimal Coastal Theme CSS Override (Option 3 Clone)
st.markdown(
    """
    <style>
    /* Background colors matching Option 3 */
    .stApp, .stApp > header {
        background-color: #F4F1EA !important;
    }
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 80px !important; /* Space for bottom nav */
    }
    /* Hide Streamlit default UI elements for app-like feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp {
        overflow-x: clip !important;
    }
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    
    /* Typography */
    h1, h2, h3, p, span, div {
        color: #1F2937 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    
    /* Center header texts */
    .app-title {
        text-align: center;
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: -10px;
        color: #1E3A8A !important;
    }
    
    /* Compact row for buttons */
    .compact-row {
        display: flex;
        gap: 12px;
        width: 100%;
        margin-top: 16px;
        margin-bottom: 16px;
    }
    
    /* Flat white buttons with black outline */
    .cam-btn {
        flex: 1;
        text-align: center;
        padding: 12px 8px;
        border-radius: 10px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        color: #1F2937 !important;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 6px;
    }
    
    /* 3 Top Stat Cards */
    .stat-card {
        flex: 1;
        padding: 12px 4px;
        border-radius: 12px !important;
        background-color: #FFFFFF !important;
        border: 1px solid #D1D5DB !important;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .stat-val-row {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 4px;
    }
    .stat-label {
        font-size: 0.65rem;
        color: #6B7280 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Custom List Forecast */
    .forecast-container {
        background: #FFFFFF;
        border: 1px solid #D1D5DB;
        border-radius: 12px;
        padding: 8px 16px;
        margin-top: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .f-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 0;
        border-bottom: 1px solid #F3F4F6;
    }
    .f-row:last-child {
        border-bottom: none;
    }
    .f-day {
        font-weight: 600;
        font-size: 0.95rem;
        width: 45px;
        color: #374151;
    }
    .f-dots {
        display: flex;
        gap: 8px;
    }
    .f-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
    }
    .f-score {
        font-size: 0.85rem;
        color: #4B5563;
        font-weight: 500;
        text-align: right;
        min-width: 85px;
    }
    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 24px;
        margin-bottom: 4px;
        color: #111827 !important;
    }
    
    /* Fake Bottom Nav Bar */
    .bottom-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        height: 65px;
        background: #FFFFFF;
        border-top: 1px solid #D1D5DB;
        display: flex;
        justify-content: space-around;
        align-items: center;
        z-index: 9999;
        padding-bottom: env(safe-area-inset-bottom);
    }
    .nav-icon {
        font-size: 22px;
        color: #9CA3AF;
    }
    .nav-icon.active {
        color: #1F2937;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Surf spots database
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

st.markdown('<div class="app-title">🌊 Surf & Wind</div>', unsafe_allow_html=True)
selected_spot_name = st.selectbox("", list(SPOTS.keys()), label_visibility="collapsed")
spot = SPOTS[selected_spot_name]
short_spot_name = selected_spot_name.split(" (")[0].split(" - ")[-1]

# 2. Side-by-side Live Cam Buttons
st.markdown(
    f"""
    <div class="compact-row">
        <a class="cam-btn" href="{spot['cam_url']}" target="_blank">📹 {short_spot_name} Cam</a>
        <a class="cam-btn" href="https://www.beachcam.co.il/" target="_blank">🎥 All Israel</a>
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
        f"&daily=sunrise,sunset&timezone=auto&forecast_days=7"
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
        return "Boardshorts"
    elif temp >= 23.0:
        return "Spring / 2mm"
    elif temp >= 20.0:
        return "3/2mm Suit"
    else:
        return "4/3mm Suit"

def format_height_with_unit(val):
    if pd.isna(val):
        return "-"
    cm = int(round(val * 100))
    ft = round(val * 3.28084, 1)
    return f"{cm} cm / {ft} ft"

def format_period_with_unit(val):
    if pd.isna(val):
        return "-"
    return f"{round(val, 1):g} s"

def format_wind_with_unit(val):
    if pd.isna(val):
        return "-"
    return f"{round(val, 1):g} km/h"

def calculate_surf_rating(row, offshore_range, onshore_range):
    h = row["Wave Height (m)"]
    p = row["Period (s)"]
    ws = row["Wind Speed (km/h)"]
    wd = row["Wind Direction (°)"]

    if pd.isna(h) or h < 0.2:
        return 1.0

    if h < 0.6:
        return round(min(4.9, 1.0 + (h / 0.6) * 3.5), 1)

    if h < 0.7:
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

    return min(10.0, max(5.0, round(height_score + period_score + wind_score, 1)))

def get_rating_hex(score):
    if score >= 7.0:
        return "#2ECC71" # Green
    elif score >= 4.0:
        return "#F39C12" # Orange
    return "#EF4444" # Red

# Load data
df, daily_df, water_temp = get_forecast_data(spot["lat"], spot["lon"])
unique_dates = sorted(df["Date"].unique())
df["DayIdx"] = df["Date"].map({d: i for i, d in enumerate(unique_dates)})

# Compute ratings and texts
df["Wind Type"] = df["Wind Direction (°)"].apply(lambda d: get_wind_type(d, spot["offshore"], spot["onshore"]))
df["Score"] = df.apply(lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1)
df["Rating"] = df["Score"].apply(lambda s: f"{s}/10")
df["Wave Height"] = df["Wave Height (m)"].apply(format_height_with_unit)
df["Swell"] = df["Swell (m)"].apply(format_height_with_unit)
df["Period"] = df["Period (s)"].apply(format_period_with_unit)
df["Wind Speed"] = df["Wind Speed (km/h)"].apply(format_wind_with_unit)

# 3. Stats Row (Exactly like Option 3 mockup)
temp_display = f"{water_temp:.1f}°C" if water_temp else "N/A"
wetsuit_advice = get_wetsuit_recommendation(water_temp)
today_sunrise = daily_df.iloc[0]["Sunrise"].strftime("%H:%M")
today_sunset = daily_df.iloc[0]["Sunset"].strftime("%H:%M")

st.markdown(
    f"""
    <div class="compact-row">
        <div class="stat-card">
            <div class="stat-val-row">🌡️ {temp_display}</div>
            <div class="stat-label">Water Temp</div>
        </div>
        <div class="stat-card">
            <div class="stat-val-row">🧍‍♂️</div>
            <div class="stat-label">{wetsuit_advice}</div>
        </div>
        <div class="stat-card">
            <div class="stat-val-row">🌅 {today_sunrise}</div>
            <div class="stat-label">Sunset {today_sunset}</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 4. Interactive Smooth Wave Height Chart
st.markdown('<div class="section-title">Wave Height</div>', unsafe_allow_html=True)
df_chart = df[df["DateTime"].dt.hour.between(6, 17)].copy()
max_wave = float(df_chart["Wave Height (m)"].max())
if pd.isna(max_wave) or max_wave <= 0:
    max_wave = 1.0

points_data = []
for _, row in df_chart.iterrows():
    val = row["Wave Height (m)"]
    points_data.append({
        "time": row["Time"],
        "day": row["Day"],
        "dayIdx": int(row["DayIdx"]),
        "hour": int(row["DateTime"].hour),
        "rating": row["Rating"],
        "ratingColor": get_rating_hex(row["Score"]),
        "wave": row["Wave Height"],
        "waveRaw": 0.0 if pd.isna(val) else float(val),
        "swell": row["Swell"],
        "period": row["Period"],
        "windType": row["Wind Type"],
        "windSpeed": row["Wind Speed"],
    })

html_chart = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {{ box-sizing: border-box; user-select: none; -webkit-tap-highlight-color: transparent; }}
  body {{ margin: 0; font-family: -apple-system, sans-serif; background: transparent; }}
  .chart-card {{
    background: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 12px 8px 0px 8px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
  }}
  .top-bar {{ display: flex; justify-content: flex-end; padding-right: 4px; margin-bottom: 4px; }}
  .hint-badge {{
    font-size: 11px; padding: 2px 8px; border-radius: 999px;
    background: #F3F4F6; color: #6B7280; font-weight: 500;
  }}
  .data-box {{
    display: none; width: 100%; margin-bottom: 12px; background: #FFFFFF;
    border: 1px solid #D1D5DB; border-radius: 10px; padding: 10px; cursor: pointer;
  }}
  .data-box.visible {{ display: block; }}
  .db-header {{
    display: flex; justify-content: space-between; font-weight: 700; font-size: 13px;
    border-bottom: 1px solid #F3F4F6; padding-bottom: 6px; margin-bottom: 8px; color: #1F2937;
  }}
  .db-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; }}
  .db-cell {{ background: #F9FAFB; border-radius: 6px; padding: 6px 4px; }}
  .db-lbl {{ font-size: 10px; color: #6B7280; margin-bottom: 2px; }}
  .db-val {{ font-weight: 700; font-size: 12px; color: #1F2937; }}
  .chart-shell {{ display: flex; position: relative; width: 100%; height: 200px; }}
  .y-axis {{
    width: 55px; flex-shrink: 0; display: flex; flex-direction: column;
    justify-content: space-between; padding: 10px 4px 30px 0; text-align: right;
    font-size: 10px; color: #9CA3AF;
  }}
  .scroll-area {{
    flex: 1; overflow-x: auto; overflow-y: hidden; touch-action: pan-x pan-y;
    position: relative; cursor: pointer; border-left: 1px solid #F3F4F6;
  }}
</style>
</head>
<body oncontextmenu="return false;">
  <div class="chart-card" id="chartCard">
    <div class="top-bar"><div class="hint-badge">Tap • Hold to drag</div></div>
    <div class="data-box" id="dataBox"></div>
    <div class="chart-shell">
      <div class="y-axis">
        <span>{format_height_with_unit(max_wave)}</span>
        <span>{format_height_with_unit(max_wave / 2.0)}</span>
        <span>0 cm</span>
      </div>
      <div class="scroll-area" id="scrollArea">
        <svg id="waveSvg" height="200"></svg>
      </div>
    </div>
  </div>
  <script>
    const points = {json.dumps(points_data)};
    const maxWave = {max_wave};
    const stepX = 26;
    const padLeft = 10, padRight = 20, padTop = 10, padBottom = 30;
    const plotHeight = 200 - padTop - padBottom;
    const svgWidth = Math.max(400, padLeft + padRight + (points.length - 1) * stepX);
    const svg = document.getElementById("waveSvg");
    svg.setAttribute("width", svgWidth);
    
    function createSvg(tag, attrs) {{
      const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
      return el;
    }}
    
    const coords = points.map((p, i) => ({{ ...p, x: padLeft + i * stepX, y: padTop + plotHeight * (1 - Math.min(1, Math.max(0, p.waveRaw / maxWave))) }}));
    
    // Day separators
    let bandStart = 0;
    for (let i = 1; i <= coords.length; i++) {{
      if (i === coords.length || coords[i].dayIdx !== coords[bandStart].dayIdx) {{
        const x1 = bandStart === 0 ? 0 : (coords[bandStart - 1].x + coords[bandStart].x) / 2;
        if (bandStart > 0) svg.appendChild(createSvg("line", {{x1: x1, y1: 0, x2: x1, y2: padTop + plotHeight, stroke: "#E5E7EB", "stroke-width": "1.5", "stroke-dasharray": "3,3"}}));
        bandStart = i;
      }}
    }}
    
    // Smooth Wave Path generation using Cubic Bezier
    let pathD = "";
    coords.forEach((c, idx) => {{
        if (idx === 0) {{ pathD += `M ${{c.x}} ${{c.y}}`; }}
        else {{
            const prev = coords[idx - 1];
            const cpX = (prev.x + c.x) / 2;
            pathD += ` C ${{cpX}} ${{prev.y}}, ${{cpX}} ${{c.y}}, ${{c.x}} ${{c.y}}`;
        }}
    }});
    
    // Fill background
    const fillD = pathD + ` L ${{coords[coords.length-1].x}} ${{padTop + plotHeight}} L ${{coords[0].x}} ${{padTop + plotHeight}} Z`;
    svg.appendChild(createSvg("path", {{ d: fillD, fill: "#E2E8F0", opacity: "0.5" }}));
    // Stroke line
    svg.appendChild(createSvg("path", {{ d: pathD, fill: "none", stroke: "#1E293B", "stroke-width": "2.5", "stroke-linecap": "round" }}));
    
    // Day Labels at exactly 12:00
    coords.forEach((c) => {{
      if (c.hour === 12) {{
        const label = createSvg("text", {{
          x: c.x, y: padTop + plotHeight + 18, fill: "#4B5563", "font-size": "11", "font-weight": "600", "text-anchor": "middle"
        }});
        label.textContent = c.day;
        svg.appendChild(label);
      }}
    }});
    
    // Interactive components
    const scrubLine = createSvg("line", {{x1: 0, y1: padTop, x2: 0, y2: padTop + plotHeight, stroke: "#1F2937", "stroke-width": "1.5", "stroke-dasharray": "3,2", opacity: "0"}});
    const activeDot = createSvg("circle", {{cx: 0, cy: 0, r: "4.5", fill: "#FFFFFF", stroke: "#1F2937", "stroke-width": "2", opacity: "0"}});
    svg.appendChild(scrubLine); svg.appendChild(activeDot);
    
    const scrollArea = document.getElementById("scrollArea"), dataBox = document.getElementById("dataBox"), chartCard = document.getElementById("chartCard");
    let selectedIdx = null, isBoxVisible = false;
    
    function syncHeight() {{ try {{ if (window.frameElement) window.frameElement.style.height = (chartCard.offsetHeight + 10) + "px"; }} catch(e){{}} }}
    function getNearestIndex(clientX) {{
      const relX = clientX - svg.getBoundingClientRect().left;
      return Math.min(coords.length - 1, Math.max(0, Math.round((relX - padLeft) / stepX)));
    }}
    
    function showData(idx) {{
      selectedIdx = idx; const c = coords[idx];
      scrubLine.setAttribute("x1", c.x); scrubLine.setAttribute("x2", c.x); scrubLine.setAttribute("opacity", "0.5");
      activeDot.setAttribute("cx", c.x); activeDot.setAttribute("cy", c.y); activeDot.setAttribute("opacity", "1");
      
      dataBox.innerHTML = `<div class="db-header"><span>${{c.time}}</span><span style="color:${{c.ratingColor}}">${{c.rating}} ⏺</span></div>
      <div class="db-grid"><div class="db-cell"><span class="db-lbl">Wave</span><span class="db-val">${{c.wave}}</span></div>
      <div class="db-cell"><span class="db-lbl">Period</span><span class="db-val">${{c.period}}</span></div>
      <div class="db-cell"><span class="db-lbl">Wind</span><span class="db-val">${{c.windSpeed}}</span></div></div>`;
      isBoxVisible = true; dataBox.classList.add("visible"); syncHeight();
    }}
    
    function hideData() {{ isBoxVisible = false; dataBox.classList.remove("visible"); scrubLine.setAttribute("opacity", "0"); activeDot.setAttribute("opacity", "0"); syncHeight(); }}
    
    scrollArea.addEventListener("click", (e) => {{
      const idx = getNearestIndex(e.clientX);
      if (isBoxVisible && idx === selectedIdx) hideData(); else showData(idx);
    }});
    
    let isScrubbing = false, touchStartX = 0, longPressTimer = null;
    scrollArea.addEventListener("touchstart", (e) => {{
      if(e.touches.length!==1) return;
      touchStartX = e.touches[0].clientX;
      longPressTimer = setTimeout(() => {{ isScrubbing = true; if(navigator.vibrate) navigator.vibrate(20); showData(getNearestIndex(touchStartX)); }}, 250);
    }}, {{passive:true}});
    
    scrollArea.addEventListener("touchmove", (e) => {{
      if(e.touches.length!==1) return;
      if(!isScrubbing) {{ if(Math.abs(e.touches[0].clientX - touchStartX) > 10) clearTimeout(longPressTimer); return; }}
      e.preventDefault(); showData(getNearestIndex(e.touches[0].clientX));
    }}, {{passive:false}});
    
    scrollArea.addEventListener("touchend", () => {{ clearTimeout(longPressTimer); isScrubbing = false; }}, {{passive:true}});
    syncHeight();
  </script>
</body>
</html>
"""
components.html(html_chart, height=310)

# 5. Daily Forecast List (Exactly like Option 3)
st.markdown('<div class="section-title">Daily Forecast</div>', unsafe_allow_html=True)

df_daylight = df[df["DateTime"].dt.hour.between(6, 17)].copy()
list_html = '<div class="forecast-container">'

for d in unique_dates:
    day_df = df_daylight[df_daylight["Date"] == d]
    if day_df.empty: continue
    
    day_name = pd.Timestamp(d).strftime("%a")
    
    # Morning (6-10), Noon (11-14), Evening (15-17)
    m_df = day_df[day_df["DateTime"].dt.hour.between(6, 10)]
    n_df = day_df[day_df["DateTime"].dt.hour.between(11, 14)]
    e_df = day_df[day_df["DateTime"].dt.hour.between(15, 17)]
    
    def get_dot_color(subset):
        if subset.empty: return "#F3F4F6"
        return get_rating_hex(subset["Score"].max())
        
    dot_m = get_dot_color(m_df)
    dot_n = get_dot_color(n_df)
    dot_e = get_dot_color(e_df)
    
    best_row = day_df.loc[day_df["Score"].idxmax()]
    best_time = best_row["HourStr"]
    best_score = best_row["Score"]
    
    list_html += f"""
    <div class="f-row">
        <div class="f-day">{day_name}</div>
        <div class="f-dots">
            <div class="f-dot" style="background:{dot_m};"></div>
            <div class="f-dot" style="background:{dot_n};"></div>
            <div class="f-dot" style="background:{dot_e};"></div>
        </div>
        <div class="f-score">{best_time} ({best_score}/10)</div>
    </div>
    """
list_html += '</div>'
st.markdown(list_html, unsafe_allow_html=True)

# 6. Bottom Navigation Bar (Visual only, to complete the Option 3 clone)
st.markdown(
    """
    <div class="bottom-nav">
        <span class="nav-icon active">🏠</span>
        <span class="nav-icon">🧭</span>
        <span class="nav-icon">🔔</span>
        <span class="nav-icon">⚙️</span>
    </div>
    """,
    unsafe_allow_html=True
)
