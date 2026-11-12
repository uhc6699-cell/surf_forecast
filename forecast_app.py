import json
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Minimal Coastal CSS
st.markdown(
    """
    <style>
    .stApp, .stApp > header {
        background-color: #F2EEE5 !important;
    }
    .block-container {
        padding: 0.5rem 1rem 80px 1rem !important;
    }
    header[data-testid="stHeader"] {display: none;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .stApp { overflow-x: clip !important; }
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    
    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #1A2B4C;
    }
    
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }
    .hamburger { font-size: 24px; color: #555; cursor: pointer; }
    .title-container { text-align: center; flex-grow: 1; }
    .main-title {
        font-size: 1.3rem; font-weight: 800; color: #1A2B4C;
        display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    
    div[data-testid="stSelectbox"] { margin-top: -15px; margin-bottom: 10px; }
    div[data-testid="stSelectbox"] > div {
        background: transparent !important; border: none !important; box-shadow: none !important;
    }
    div[data-testid="stSelectbox"] * {
        color: #4B5563 !important; text-align: center !important; font-size: 0.95rem !important; font-weight: 600 !important;
    }
    
    .cam-buttons { display: flex; gap: 12px; margin-bottom: 16px; }
    .cam-btn-dark, .cam-btn-light {
        flex: 1; padding: 12px 10px; border-radius: 8px; text-align: center;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 600;
        display: flex; align-items: center; justify-content: center; gap: 6px;
    }
    .cam-btn-dark { background-color: #1A2B4C; color: #FFFFFF !important; }
    .cam-btn-light { background-color: transparent; border: 1px solid #1A2B4C; color: #1A2B4C !important; }
    
    .unified-stat-card {
        background: #FFFFFF; border-radius: 16px; padding: 14px 10px;
        display: flex; justify-content: space-around; align-items: center;
        margin-bottom: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .stat-col { text-align: center; flex: 1; }
    .stat-main { font-size: 1.15rem; font-weight: 700; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; gap: 4px; line-height: 1.3; }
    .stat-sub { font-size: 0.75rem; font-weight: 600; color: #6B7280 !important; }
    
    [data-testid="stDataFrame"] {
        background-color: #FFFFFF !important;
        border-radius: 12px !important;
        padding: 4px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        margin-bottom: 10px;
    }
    [data-testid="stDataFrame"] > div { border: none !important; }
    .day-header {
        font-size: 1.1rem; font-weight: 800; color: #1A2B4C;
        margin-top: 20px; margin-bottom: 8px; padding-left: 10px;
        border-left: 4px solid #1A2B4C;
    }
    
    .bottom-nav {
        position: fixed; bottom: 0; left: 0; right: 0; height: 75px;
        background: #FFFFFF; border-top: 1px solid #E5E7EB;
        display: flex; justify-content: space-around; align-items: center;
        z-index: 9999; padding-bottom: env(safe-area-inset-bottom);
    }
    .nav-icon { font-size: 24px; color: #9CA3AF; }
    .nav-icon.active { color: #1A2B4C; }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom Header
st.markdown(
    """
    <div class="custom-header">
        <div class="hamburger">≡</div>
        <div class="title-container"><div class="main-title">🌊 Surf & Wind</div></div>
        <div style="width: 24px;"></div>
    </div>
    """, unsafe_allow_html=True
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

st.markdown(
    f"""
    <div class="cam-buttons">
        <a class="cam-btn-dark" href="{spot['cam']}" target="_blank">📹 {short_spot_name} Cam</a>
        <a class="cam-btn-light" href="https://www.beachcam.co.il/" target="_blank">📹 All Israel Cams</a>
    </div>
    """, unsafe_allow_html=True
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

def get_wetsuit_icon_text(temp):
    if temp is None or pd.isna(temp): return "❓", "N/A"
    if temp >= 26.0: return "🩳", "Boardshorts"
    if temp >= 23.0: return "🏄‍♂️", "Spring / 2mm"
    if temp >= 20.0: return "👕", "3/2mm Suit"
    return "🥶", "4/3mm Suit"

def is_angle_in_range(angle, start, end):
    if start <= end: return start <= angle <= end
    return angle >= start or angle <= end

def get_wind_type(direction, offshore_range, onshore_range):
    if pd.isna(direction): return ""
    if is_angle_in_range(direction, *offshore_range): return "Offshore 💨"
    elif is_angle_in_range(direction, *onshore_range): return "Onshore 🌊"
    return "Cross-shore"

def format_height_with_unit(val):
    if pd.isna(val): return "-"
    cm, ft = int(round(val * 100)), round(val * 3.28084, 1)
    return f"{cm} cm / {ft} ft"

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

def get_rating_tier(score):
    if score >= 7.0: return "green", "#48BB78", "rgba(72, 187, 120, 0.2)", "🟢"
    elif score >= 4.0: return "orange", "#ECC94B", "rgba(236, 201, 75, 0.25)", "🟠"
    return "red", "#F56565", "rgba(245, 101, 101, 0.2)", "🔴"

def format_rating_badge(score):
    _, _, _, icon = get_rating_tier(score)
    return f"{score}/10 {icon}"

def style_forecast_table(source_df, cols):
    display_df = source_df[cols].copy()
    scores = source_df["Score"]
    def highlight_rating(row):
        s = scores.loc[row.name]
        _, text_hex, bg_rgba, _ = get_rating_tier(s)
        rating_css = f"background-color: {bg_rgba}; color: #1A2B4C; font-weight: 700;"
        return [rating_css if col == "Rating" else "" for col in row.index]
    return display_df.style.apply(highlight_rating, axis=1)

def get_full_table_height(num_rows):
    return (num_rows + 1) * 35 + 8

def build_day_period_summary(day_df):
    periods = [("🌅 Morning", 6, 10), ("☀️ Noon", 11, 14), ("🌇 Evening", 15, 19)]
    summary_rows = []
    for label, start_h, end_h in periods:
        subset = day_df[day_df["DateTime"].dt.hour.between(start_h, end_h)]
        if subset.empty: continue
        best_idx = subset["Score"].idxmax()
        rep_row = subset.loc[best_idx].copy()
        rep_row["Session"] = label
        summary_rows.append(rep_row)
    return pd.DataFrame(summary_rows) if summary_rows else pd.DataFrame()

df, daily_df, water_temp = get_forecast_data(spot["lat"], spot["lon"])
unique_dates = sorted(df["Date"].unique())
df["DayIdx"] = df["Date"].map({d: i for i, d in enumerate(unique_dates)})
df["Wind Type"] = df["Wind Direction (°)"].apply(lambda d: get_wind_type(d, spot["offshore"], spot["onshore"]))
df["Score"] = df.apply(lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1)
df["Rating"] = df["Score"].apply(format_rating_badge)
df["Wave Height"] = df["Wave Height (m)"].apply(format_height_with_unit)
df["Swell"] = df["Swell (m)"].apply(format_height_with_unit)
df["Period"] = df["Period (s)"].apply(lambda p: f"{round(p, 1):g} s" if not pd.isna(p) else "-")
df["Wind Speed"] = df["Wind Speed (km/h)"].apply(lambda s: f"{round(s, 1):g} km/h" if not pd.isna(s) else "-")

# Stats Card in English
temp_str = f"{water_temp:.1f}°C" if water_temp else "N/A"
suit_icon, suit_text = get_wetsuit_icon_text(water_temp)
today_sunrise = daily_df.iloc[0]["Sunrise"].strftime("%H:%M")
today_sunset = daily_df.iloc[0]["Sunset"].strftime("%H:%M")

st.markdown(
    f"""
    <div class="unified-stat-card">
        <div class="stat-col">
            <div class="stat-main">🌡️ {temp_str}</div>
            <div class="stat-sub">Water Temp</div>
        </div>
        <div class="stat-col">
            <div class="stat-main">{suit_icon}</div>
            <div class="stat-sub">{suit_text}</div>
        </div>
        <div class="stat-col">
            <div class="stat-main" style="font-size: 0.95rem; line-height: 1.4;">🌅 {today_sunrise}<br>🌇 {today_sunset}</div>
            <div class="stat-sub">Sunrise / Sunset</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# Smooth Wave Chart with multiple Y-axis labels and centered Day names at the top
df_chart = df[df["DateTime"].dt.hour.between(6, 17)].copy()
max_wave_m = float(df_chart["Wave Height (m)"].max())
if pd.isna(max_wave_m) or max_wave_m <= 0: max_wave_m = 1.0

y_top_label = format_height_with_unit(max_wave_m)
y_three_q_label = format_height_with_unit(max_wave_m * 0.75)
y_mid_label = format_height_with_unit(max_wave_m * 0.5)
y_one_q_label = format_height_with_unit(max_wave_m * 0.25)

points_data = []
for _, row in df_chart.iterrows():
    val = row["Wave Height (m)"]
    _, hex_color, _, _ = get_rating_tier(row["Score"])
    points_data.append({
        "time": row["Time"], "day": row["Day"], "hour": int(row["DateTime"].hour),
        "dayIdx": int(row["DayIdx"]), "ratingColor": hex_color, "rating": row["Rating"],
        "wave": row["Wave Height"], "swell": row["Swell"], "period": row["Period"],
        "windType": row["Wind Type"], "windSpeed": row["Wind Speed"],
        "waveRaw": 0.0 if pd.isna(val) else float(val)
    })

html_chart = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {{ box-sizing: border-box; user-select: none; -webkit-tap-highlight-color: transparent; }}
  body {{ margin: 0; font-family: -apple-system, sans-serif; background: transparent; }}
  .chart-card {{ background: #FFFFFF; border-radius: 16px; padding: 16px 8px 10px 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); }}
  .c-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; padding: 0 4px; }}
  .c-title {{ font-size: 1.05rem; font-weight: 800; color: #1A2B4C; }}
  .hint-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 999px; background: #F3F4F6; color: #6B7280; font-weight: 600; }}
  
  .data-box {{ display: none; width: 100%; margin-bottom: 12px; background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.04); }}
  .data-box.visible {{ display: block; }}
  .db-header {{ display: flex; justify-content: space-between; font-weight: 800; font-size: 13px; border-bottom: 1px solid #F3F4F6; padding-bottom: 6px; margin-bottom: 8px; color: #1A2B4C; }}
  .db-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; text-align: center; }}
  .db-cell {{ background: #F9FAFB; border-radius: 8px; padding: 6px 4px; }}
  .db-lbl {{ font-size: 10px; color: #6B7280; margin-bottom: 2px; font-weight: 600;}}
  .db-val {{ font-weight: 800; font-size: 12px; color: #1A2B4C; }}
  .close-btn {{ cursor: pointer; padding: 0 4px; }}
  
  .chart-shell {{ display: flex; position: relative; width: 100%; height: 185px; }}
  .y-axis {{
    width: 65px; flex-shrink: 0; display: flex; flex-direction: column;
    justify-content: space-between; padding: 15px 6px 35px 0; text-align: right;
    font-size: 9px; font-weight: 600; color: #6B7280; border-right: 1px solid #F3F4F6;
  }}
  .scroll-area {{
    flex: 1; overflow-x: auto; overflow-y: hidden; touch-action: pan-x pan-y;
    position: relative; cursor: pointer;
  }}
</style>
</head>
<body oncontextmenu="return false;">
  <div class="chart-card" id="chartCard">
    <div class="c-header">
      <div class="c-title">Wave Height</div>
      <div class="hint-badge">Tap & Drag</div>
    </div>
    <div class="data-box" id="dataBox"></div>
    <div class="chart-shell">
      <div class="y-axis">
        <span>{y_top_label}</span>
        <span>{y_three_q_label}</span>
        <span>{y_mid_label}</span>
        <span>{y_one_q_label}</span>
        <span>0 cm</span>
      </div>
      <div class="scroll-area" id="scrollArea">
        <svg id="waveSvg" height="185"></svg>
      </div>
    </div>
  </div>
  <script>
    const points = {json.dumps(points_data)};
    const maxWave = {max_wave_m};
    const stepX = 28, padLeft = 14, padRight = 20, padTop = 18, padBottom = 38;
    const plotHeight = 185 - padTop - padBottom;
    const svgWidth = Math.max(400, padLeft + padRight + (points.length - 1) * stepX);
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
    
    let bandStart = 0;
    for (let i = 1; i <= coords.length; i++) {{
      if (i === coords.length || coords[i].dayIdx !== coords[bandStart].dayIdx) {{
        const x1 = bandStart === 0 ? 0 : (coords[bandStart - 1].x + coords[bandStart].x) / 2;
        const x2 = i === coords.length ? svgWidth : (coords[i - 1].x + coords[i].x) / 2;
        
        if (bandStart > 0) {{
          svg.appendChild(createSvg("line", {{ x1: x1, y1: 0, x2: x1, y2: padTop + plotHeight, stroke: "#CBD5E1", "stroke-width": "1.5", "stroke-dasharray": "4,4" }}));
        }}
        
        const midX = (x1 + x2) / 2;
        const dayLabel = createSvg("text", {{ x: midX, y: padTop + 2, fill: "#1A2B4C", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }});
        dayLabel.textContent = coords[bandStart].day;
        svg.appendChild(dayLabel);
        
        bandStart = i;
      }}
    }}
    
    let pathD = "";
    coords.forEach((c, idx) => {{
        if (idx === 0) pathD += `M ${{c.x}} ${{c.y}}`;
        else {{
            const prev = coords[idx - 1]; const cpX = (prev.x + c.x) / 2;
            pathD += ` C ${{cpX}} ${{prev.y}}, ${{cpX}} ${{c.y}}, ${{c.x}} ${{c.y}}`;
        }}
    }});
    
    const fillD = pathD + ` L ${{coords[coords.length-1].x}} ${{padTop + plotHeight}} L ${{coords[0].x}} ${{padTop + plotHeight}} Z`;
    svg.appendChild(createSvg("path", {{ d: fillD, fill: "url(#waveGrad)" }}));
    svg.appendChild(createSvg("path", {{ d: pathD, fill: "none", stroke: "#1A2B4C", "stroke-width": "3", "stroke-linecap": "round" }}));
    
    coords.forEach(c => {{
      if (c.hour === 6 || c.hour === 12 || c.hour === 17) {{
        svg.appendChild(createSvg("circle", {{ cx: c.x, cy: c.y, r: "5", fill: "#FFFFFF", stroke: c.ratingColor, "stroke-width": "2.5" }}));
        const label = createSvg("text", {{ x: c.x, y: padTop + plotHeight + 18, fill: "#4B5563", "font-size": "10", "font-weight": "700", "text-anchor": "middle" }});
        label.textContent = c.time.split(" ")[1];
        svg.appendChild(label);
      }}
    }});
    
    const scrubLine = createSvg("line", {{x1: 0, y1: 0, x2: 0, y2: padTop + plotHeight, stroke: "#1A2B4C", "stroke-width": "1.5", "stroke-dasharray": "3,2", opacity: "0"}});
    const activeDot = createSvg("circle", {{cx: 0, cy: 0, r: "5.5", fill: "#FFFFFF", stroke: "#1A2B4C", "stroke-width": "2.5", opacity: "0"}});
    svg.appendChild(scrubLine); svg.appendChild(activeDot);
    
    const scrollArea = document.getElementById("scrollArea"), dataBox = document.getElementById("dataBox"), chartCard = document.getElementById("chartCard");
    let selectedIdx = null, isBoxVisible = false;
    
    function syncHeight() {{ try {{ if (window.frameElement) window.frameElement.style.height = (chartCard.offsetHeight + 10) + "px"; }} catch(e){{}} }}
    function getNearestIndex(clientX) {{
      const relX = clientX - svg.getBoundingClientRect().left;
      return Math.min(coords.length - 1, Math.max(0, Math.round((relX - padLeft) / stepX)));
    }}
    
    window.hideData = function() {{
      isBoxVisible = false; dataBox.classList.remove("visible");
      scrubLine.setAttribute("opacity", "0"); activeDot.setAttribute("opacity", "0"); syncHeight();
    }};
    
    function showData(idx) {{
      selectedIdx = idx; const c = coords[idx];
      scrubLine.setAttribute("x1", c.x); scrubLine.setAttribute("x2", c.x); scrubLine.setAttribute("opacity", "0.5");
      activeDot.setAttribute("cx", c.x); activeDot.setAttribute("cy", c.y); activeDot.setAttribute("opacity", "1");
      
      dataBox.innerHTML = `
        <div class="db-header">
            <span>${{c.time}}</span>
            <span style="color:${{c.ratingColor}}">${{c.rating}}</span>
            <span class="close-btn" onclick="hideData()">✕</span>
        </div>
        <div class="db-grid">
            <div class="db-cell"><span class="db-lbl">Wave</span><span class="db-val">${{c.wave}}</span></div>
            <div class="db-cell"><span class="db-lbl">Swell</span><span class="db-val">${{c.swell}}</span></div>
            <div class="db-cell"><span class="db-lbl">Period</span><span class="db-val">${{c.period}}</span></div>
            <div class="db-cell"><span class="db-lbl">Wind</span><span class="db-val">${{c.windType}}</span></div>
            <div class="db-cell"><span class="db-lbl">Speed</span><span class="db-val">${{c.windSpeed}}</span></div>
        </div>
      `;
      isBoxVisible = true; dataBox.classList.add("visible"); syncHeight();
    }}
    
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
components.html(html_chart, height=325)

# Daily Tables
st.markdown('<div class="day-header" style="margin-top: 5px;">Daily Tables</div>', unsafe_allow_html=True)
summary_cols = ["Session", "Rating", "Wave Height", "Swell", "Period", "Wind Type", "Wind Speed"]
hourly_cols = ["HourStr", "Rating", "Wave Height", "Swell", "Period", "Wind Type", "Wind Speed"]

df_daylight = df[
    (df["DateTime"] >= (df["Sunrise"] - pd.Timedelta(minutes=30))) & 
    (df["DateTime"] <= (df["Sunset"] + pd.Timedelta(minutes=30)))
].copy()

for i, d in enumerate(unique_dates):
    day_full_df = df[df["Date"] == d].copy()
    day_dl_df = df_daylight[df_daylight["Date"] == d].copy()

    day_ts = pd.Timestamp(d)
    if i == 0: day_title = f"Today — {day_ts.strftime('%A (%d/%m)')}"
    elif i == 1: day_title = f"Tomorrow — {day_ts.strftime('%A (%d/%m)')}"
    else: day_title = day_ts.strftime("%A (%d/%m)")

    st.markdown(f'<div class="day-header">{day_title}</div>', unsafe_allow_html=True)

    summary_df = build_day_period_summary(day_full_df)
    if not summary_df.empty:
        st.dataframe(
            style_forecast_table(summary_df, summary_cols),
            hide_index=True,
            height=get_full_table_height(len(summary_df)),
        )

    with st.expander(f"All Daylight Hours — {day_ts.strftime('%A')}"):
        hourly_display_df = day_dl_df[hourly_cols].rename(columns={"HourStr": "Hour"})
        st.dataframe(
            style_forecast_table(hourly_display_df, ["Hour"] + summary_cols[1:]),
            hide_index=True,
            height=get_full_table_height(len(day_dl_df)),
        )

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
