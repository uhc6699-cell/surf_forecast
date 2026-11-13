import json
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd
import datetime
import time

# Initialize Theme & Unit State
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "unit" not in st.session_state:
    st.session_state.unit = "metric"

st.set_page_config(
    page_title="Surf & Wind Forecast", 
    page_icon="🌊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dynamic Theme Colors
is_dark = st.session_state.theme == "dark"

bg_color = "#0F172A" if is_dark else "#F2EEE5"
card_bg = "#1E293B" if is_dark else "#FFFFFF"
text_color = "#F8FAFC" if is_dark else "#1A2B4C"
sub_text = "#94A3B8" if is_dark else "#6B7280"
border_color = "#334155" if is_dark else "#E5E7EB"
chart_line = "#38BDF8" if is_dark else "#1A2B4C"
chart_grad_top = "#38BDF8" if is_dark else "#8997A8"
grid_color = "#334155" if is_dark else "#CBD5E1"
db_cell_bg = "#0F172A" if is_dark else "#F9FAFB"

active_bg = text_color
active_fg = bg_color
inactive_bg = card_bg
inactive_fg = text_color

# Coastal & Dynamic Theme CSS
st.markdown(
    f"""
    <style>
    :root {{
        color-scheme: {"dark" if is_dark else "light"} !important;
    }}
    
    .stApp, .stApp > header {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}
    .block-container {{
        padding: 0.5rem 1rem 30px 1rem !important;
    }}
    header[data-testid="stHeader"] {{display: none;}}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    .stApp {{ overflow-x: clip !important; }}
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {{
        min-width: 0 !important;
        max-width: 100% !important;
    }}
    
    * {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: {text_color} !important;
    }}
    
    .custom-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }}
    .hamburger {{ font-size: 24px; cursor: pointer; }}
    .title-container {{ text-align: center; flex-grow: 1; }}
    .main-title {{
        font-size: 1.3rem; font-weight: 800;
        display: flex; align-items: center; justify-content: center; gap: 6px;
    }}
    
    div[data-testid="stSelectbox"] {{ margin-top: -10px; margin-bottom: 10px; }}
    div[data-testid="stSelectbox"] > div {{
        background: {card_bg} !important; border: 1px solid {border_color} !important; border-radius: 8px !important; box-shadow: none !important;
    }}
    div[data-testid="stSelectbox"] * {{
        color: {text_color} !important; text-align: center !important; font-size: 0.95rem !important; font-weight: 600 !important;
    }}
    
    .cam-buttons {{ display: flex; gap: 12px; margin-bottom: 16px; }}
    .cam-btn-dark, .cam-btn-light {{
        flex: 1; padding: 12px 10px; border-radius: 8px; text-align: center;
        text-decoration: none !important; font-size: 0.85rem; font-weight: 600;
        display: flex; align-items: center; justify-content: center; gap: 6px;
    }}
    .cam-btn-dark {{ background-color: {text_color}; color: {bg_color} !important; }}
    .cam-btn-light {{ background-color: {card_bg}; border: 1px solid {text_color}; color: {text_color} !important; }}
    
    .unified-stat-card {{
        background: {card_bg}; border-radius: 16px; padding: 14px 10px;
        display: flex; justify-content: space-around; align-items: center;
        margin-bottom: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border: 1px solid {border_color};
    }}
    .stat-col {{ text-align: center; flex: 1; }}
    .stat-main {{ font-size: 1.15rem; font-weight: 700; margin-bottom: 2px; display: flex; align-items: center; justify-content: center; gap: 4px; line-height: 1.3; }}
    .stat-sub {{ font-size: 0.75rem; font-weight: 600; color: {sub_text} !important; }}
    
    .day-header {{
        font-size: 1.1rem; font-weight: 800;
        margin-top: 24px; margin-bottom: 12px; padding-left: 10px;
        border-left: 4px solid {text_color};
    }}
    
    /* Layout fix for Columns - Forces Unit Switcher buttons side-by-side on mobile */
    div[data-testid="stHorizontalBlock"] {{
        flex-wrap: nowrap !important;
        gap: 12px !important;
        align-items: center !important;
    }}
    div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {{
        min-width: 0 !important; 
    }}

    /* Buttons Style for Unit Selector */
    div[data-testid="stButton"] button {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 12px 10px !important;
        height: auto !important;
        min-height: 40px !important;
        width: 100% !important;
        border: 1px solid {text_color} !important;
    }}
    div[data-testid="stButton"] button p {{
        font-size: 0.85rem !important;
        margin: 0 !important;
    }}

    /* Horizontal Scroll Table Styles */
    .sf-table-wrapper {{
        background: {card_bg};
        border-radius: 12px;
        border: 1px solid {border_color};
        margin-bottom: 4px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
    }}
    .sf-table-container {{
        min-width: 650px; /* Forces Horizontal scroll */
        display: flex;
        flex-direction: column;
    }}
    .sf-header-row {{
        display: grid;
        grid-template-columns: 60px 1.2fr 1.3fr 1fr 90px 75px 65px;
        border-bottom: 1px solid {border_color};
        text-align: center;
        font-size: 0.75rem;
        font-weight: 700;
        color: {sub_text};
        background: {db_cell_bg};
    }}
    .sf-row {{
        display: grid;
        grid-template-columns: 60px 1.2fr 1.3fr 1fr 90px 75px 65px;
        border-bottom: 1px solid {border_color};
        align-items: stretch;
        text-align: center;
    }}
    .sf-row:last-child {{ border-bottom: none; }}
    
    /* Vertical Dividers */
    .sf-header-row > div, .sf-row > div {{
        padding: 10px 4px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }}
    .sf-header-row > div:not(:last-child), .sf-row > div:not(:last-child) {{
        border-right: 1px solid {border_color};
    }}
    
    .sf-time {{ font-size: 0.8rem; font-weight: 600; color: {sub_text}; }}
    .sf-val-main {{ font-size: 0.95rem; font-weight: 800; margin-bottom: 2px; }}
    .sf-val-sub {{ font-size: 0.75rem; font-weight: 600; color: {text_color}; }}
    
    .rating-badge {{
        display: inline-block; font-size: 0.65rem; font-weight: 800;
        padding: 2px 6px; border-radius: 4px; margin-top: 4px; text-transform: uppercase;
    }}
    
    .wind-arrow-container {{
        display: flex; align-items: center; justify-content: center; gap: 4px;
        font-size: 0.95rem; font-weight: 800; color: {text_color};
    }}
    .wind-arrow {{ display: inline-block; font-size: 1rem; }}
    
    /* Clean up Streamlit Expander */
    [data-testid="stExpander"] {{ border: none !important; box-shadow: none !important; background: transparent !important; margin-top: 0px; margin-bottom: 20px; }}
    [data-testid="stExpander"] summary {{ background: {db_cell_bg}; border-radius: 8px; border: 1px solid {border_color}; padding: 10px; }}
    [data-testid="stExpander"] summary p {{ font-weight: 700; color: {text_color}; font-size: 0.85rem; }}
    [data-testid="stExpander"] .streamlit-expanderContent {{ padding: 0 !important; margin-top: 4px; }}
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

# Centered Spot Selector & Dark Mode Toggle
selected_spot_name = st.selectbox("", list(SPOTS.keys()), label_visibility="collapsed")
new_theme = st.toggle("Dark Mode", value=is_dark, key="theme_toggle")

if new_theme != is_dark:
    st.session_state.theme = "dark" if new_theme else "light"
    st.rerun()

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
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
        f"&hourly=wind_speed_10m,wind_direction_10m,temperature_2m,weather_code,uv_index"
        f"&daily=sunrise,sunset&timezone=auto&forecast_days=7"
    )
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # מנסים למשוך את הנתונים
            wave_response = requests.get(marine_url, timeout=15)
            wave_response.raise_for_status()
            wave_data = wave_response.json()

            weather_response = requests.get(weather_url, timeout=15)
            weather_response.raise_for_status()
            wind_data = weather_response.json()
            
            # אם הגענו לפה, הכל עבד פיקס - שוברים את הלולאה וממשיכים
            break
            
        except requests.exceptions.RequestException:
            # אם יש שגיאה, מחכים 2 שניות ומנסים שוב (אלא אם זה הניסיון האחרון)
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            else:
                st.warning("⏳ שרת הנתונים לא מגיב כרגע גם לאחר מספר ניסיונות. אנא רענן את העמוד מאוחר יותר.")
                st.stop()

    df = pd.DataFrame({
        "DateTime": pd.to_datetime(wave_data["hourly"]["time"]),
        "Wave Height (m)": wave_data["hourly"]["wave_height"],
        "Swell (m)": wave_data["hourly"]["swell_wave_height"],
        "Period (s)": wave_data["hourly"]["wave_period"],
        "Water Temp (°C)": wave_data["hourly"]["sea_surface_temperature"],
        "Wind Speed (km/h)": wind_data["hourly"]["wind_speed_10m"],
        "Wind Direction (°)": wind_data["hourly"]["wind_direction_10m"],
        "Air Temp (°C)": wind_data["hourly"]["temperature_2m"],
        "Weather Code": wind_data["hourly"]["weather_code"],
        "UV Index": wind_data["hourly"]["uv_index"],
    })
    df["Date"] = df["DateTime"].dt.date
    df["Day"] = df["DateTime"].dt.strftime("%a")
    df["HourStr"] = df["DateTime"].dt.strftime("%H:%M")
    df["Time"] = df["DateTime"].dt.strftime("%a %H:00")

    daily_df = pd.DataFrame({
        "Date": pd.to_datetime(wind_data["daily"]["time"]).date,
        "Sunrise": pd.to_datetime(wind_data["daily"]["sunrise"]),
        "Sunset": pd.to_datetime(wind_data["daily"]["sunset"]),
    })
    
    df = df.merge(daily_df, on="Date", how="left")

    water_temp = wave_data.get("current", {}).get("sea_surface_temperature")
    if water_temp is None:
        sst_series = pd.Series(wave_data["hourly"].get("sea_surface_temperature", [])).dropna()
        water_temp = float(sst_series.iloc[0]) if not sst_series.empty else None

    return df, daily_df, water_temp

    df = pd.DataFrame({
        "DateTime": pd.to_datetime(wave_data["hourly"]["time"]),
        "Wave Height (m)": wave_data["hourly"]["wave_height"],
        "Swell (m)": wave_data["hourly"]["swell_wave_height"],
        "Period (s)": wave_data["hourly"]["wave_period"],
        "Water Temp (°C)": wave_data["hourly"]["sea_surface_temperature"],
        "Wind Speed (km/h)": wind_data["hourly"]["wind_speed_10m"],
        "Wind Direction (°)": wind_data["hourly"]["wind_direction_10m"],
        "Air Temp (°C)": wind_data["hourly"]["temperature_2m"],
        "Weather Code": wind_data["hourly"]["weather_code"],
        "UV Index": wind_data["hourly"]["uv_index"],
    })
    df["Date"] = df["DateTime"].dt.date
    df["Day"] = df["DateTime"].dt.strftime("%a")
    df["HourStr"] = df["DateTime"].dt.strftime("%H:%M")
    df["Time"] = df["DateTime"].dt.strftime("%a %H:00")

    daily_df = pd.DataFrame({
        "Date": pd.to_datetime(wind_data["daily"]["time"]).date,
        "Sunrise": pd.to_datetime(wind_data["daily"]["sunrise"]),
        "Sunset": pd.to_datetime(wind_data["daily"]["sunset"]),
    })
    
    df = df.merge(daily_df, on="Date", how="left")

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

def get_rating_details(score, is_dark_theme):
    if score >= 7.0: 
        return "GOOD", ("#4ADE80" if is_dark_theme else "#15803D"), "rgba(72, 187, 120, 0.15)"
    elif score >= 5.0: 
        return "FAIR", ("#FBBF24" if is_dark_theme else "#B45309"), "rgba(236, 201, 75, 0.15)"
    elif score >= 3.5:
        return "POOR", ("#F87171" if is_dark_theme else "#B91C1C"), "rgba(245, 101, 101, 0.15)"
    return "VERY POOR", ("#F87171" if is_dark_theme else "#B91C1C"), "rgba(245, 101, 101, 0.15)"

def get_weather_icon(code):
    if pd.isna(code): return ""
    c = int(code)
    if c == 0: return "☀️"
    elif c in [1, 2]: return "⛅"
    elif c == 3: return "☁️"
    elif c in [45, 48]: return "🌫️"
    elif c in [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82]: return "🌧️"
    elif c in [71, 73, 75, 77, 85, 86]: return "❄️"
    elif c in [95, 96, 99]: return "⛈️"
    return "🌥️"

df, daily_df, water_temp = get_forecast_data(spot["lat"], spot["lon"])
unique_dates = sorted(df["Date"].unique())
df["DayIdx"] = df["Date"].map({d: i for i, d in enumerate(unique_dates)})
df["Score"] = df.apply(lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1)
unit_sys = st.session_state.unit

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

# Smooth Wave Chart - Include all hours to show night continuity, with a very minimal gap
max_wave_m = 2.0

if unit_sys == "metric":
    y_labels = [f"{v}" for v in range(200, -1, -50)]
    ax_unit = "cm"
else:
    y_labels = [f"{round((v/100)*3.28084, 1)}" for v in range(200, -1, -50)]
    ax_unit = "ft"

y_spans = "".join([f"<span>{lbl}</span>" for lbl in y_labels])

def fmt_chart_tooltip(val, u_sys):
    if pd.isna(val): return "-"
    if u_sys == "metric":
        return f"{int(round(val * 100))} cm"
    else:
        return f"{round(val * 3.28084, 1)} ft"

points_data = []
prev_day_idx = None

# סינון: לוקחים נתון רק כל 3 שעות. זה מה שיהפוך את הגרף לחלק ועגול לחלוטין.
df_chart = df[df["DateTime"].dt.hour % 3 == 0]

for _, row in df_chart.iterrows():
    val = row["Wave Height (m)"]
    _, hex_color, _ = get_rating_details(row["Score"], is_dark)
    current_day_idx = int(row["DayIdx"])
    
    if prev_day_idx is not None and current_day_idx != prev_day_idx:
        points_data.append({
            "isGap": True,
            "day": row["Day"],
            "dayIdx": current_day_idx
        })
    prev_day_idx = current_day_idx

    hour_val = int(row["DateTime"].hour)
    # שינינו ל-18 במקום 17 כדי לקבל סימטריה מוחלטת על הגרף (6 בבוקר, 12 באמצע, 18 בערב)
    is_marked_hour = (hour_val in [6, 12, 18])

    points_data.append({
        "isGap": False,
        "time": row["Time"], "day": row["Day"], "hour": hour_val,
        "dayIdx": current_day_idx, "ratingColor": hex_color, "rating": f"{row['Score']}/10",
        "wave": fmt_chart_tooltip(val, unit_sys), "swell": fmt_chart_tooltip(row["Swell (m)"], unit_sys), 
        "period": f"{round(row['Period (s)'],1)}s" if not pd.isna(row["Period (s)"]) else "-",
        "windSpeed": f"{round(row['Wind Speed (km/h)'],1)} km/h" if not pd.isna(row["Wind Speed (km/h)"]) else "-",
        "waveRaw": 0.0 if pd.isna(val) else float(val),
        "isMarkedHour": is_marked_hour
    })

html_chart = f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * {{ box-sizing: border-box; user-select: none; -webkit-tap-highlight-color: transparent; }}
  body {{ margin: 0; font-family: -apple-system, sans-serif; background: transparent; overflow: hidden; }}
  .chart-card {{ background: {card_bg}; border-radius: 16px; padding: 16px 8px 10px 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.03); border: 1px solid {border_color}; position: relative; }}
  .c-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; padding: 0 4px; }}
  .c-title {{ font-size: 1.05rem; font-weight: 800; color: {text_color}; }}
  .hint-badge {{ font-size: 11px; padding: 2px 8px; border-radius: 999px; background: {db_cell_bg}; color: {sub_text}; font-weight: 600; border: 1px solid {border_color}; }}
  
  .data-box {{ 
      height: 65px; margin-bottom: 12px; background: {card_bg}; border: 1px solid {border_color}; 
      border-radius: 12px; padding: 8px 10px; visibility: hidden; opacity: 0; transition: opacity 0.15s ease;
  }}
  .data-box.visible {{ visibility: visible; opacity: 1; }}
  .db-header {{ display: flex; justify-content: space-between; font-weight: 800; font-size: 13px; border-bottom: 1px solid {border_color}; padding-bottom: 4px; margin-bottom: 6px; color: {text_color}; }}
  .db-grid {{ display: flex; justify-content: space-around; text-align: center; gap: 10px; }}
  .db-cell {{ flex: 1; background: {db_cell_bg}; border-radius: 8px; padding: 4px; border: 1px solid {border_color}; font-size: 11px; color: {sub_text}; font-weight: 600; }}
  .db-val {{ font-weight: 800; font-size: 12px; color: {text_color}; }}
  .close-btn {{ cursor: pointer; padding: 0 4px; color: {text_color}; }}
  
  .chart-shell {{ display: flex; position: relative; width: 100%; height: 185px; }}
  .y-axis {{
    width: 35px; flex-shrink: 0; display: flex; flex-direction: column;
    justify-content: space-between; padding: 22px 4px 34px 0; text-align: right;
    font-size: 9px; font-weight: 600; color: {sub_text}; border-right: 1px solid {border_color};
    line-height: 1;
  }}
  .scroll-area {{
    flex: 1; overflow-x: auto; overflow-y: hidden; touch-action: pan-x pan-y;
    position: relative; cursor: crosshair;
  }}
</style>
</head>
<body oncontextmenu="return false;">
  <div class="chart-card" id="chartCard">
    <div class="c-header">
      <div class="c-title">Wave Height ({ax_unit})</div>
      <div class="hint-badge">Long Press to Drag</div>
    </div>
    <div class="data-box" id="dataBox"></div>
    <div class="chart-shell">
      <div class="y-axis">
        {y_spans}
      </div>
      <div class="scroll-area" id="scrollArea">
        <svg id="waveSvg" height="185"></svg>
      </div>
    </div>
  </div>
  <script>
    const rawPoints = {json.dumps(points_data)};
    const maxWave = {max_wave_m};
    
  const normalStepX = 21; // הגדלנו מ-7 ל-21 כי עכשיו יש פחות נקודות ביום
    const gapStepX = 2;
    const padLeft = 14, padRight = 20, padTop = 26, padBottom = 38;
    
    let currentX = padLeft;
    const coords = rawPoints.map((p, i) => {{
      if (p.isGap) {{
        currentX += gapStepX;
        return {{ ...p, x: currentX }};
     }} else {{
        if (i > 0) currentX += normalStepX;
        return {{ 
          ...p, 
          x: currentX, 
          /* שינוי: הוספנו 0.04 במקום 0 כדי לשמור על קצת נפח ויזואלי גם כשהגלים שטוחים */
          y: padTop + (185 - padTop - padBottom) * (1 - Math.min(1, Math.max(0.04, p.waveRaw / maxWave))) 
        }};
      }}
    
    const svgWidth = Math.max(400, currentX + padRight);
    const svg = document.getElementById("waveSvg");
    svg.setAttribute("width", svgWidth);
    
   const defs = document.createElementNS("http://www.w3.org/2000/svg", "defs");
    defs.innerHTML = `<linearGradient id="waveGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="{chart_grad_top}" stop-opacity="0.85"/>
      <stop offset="100%" stop-color="{card_bg}" stop-opacity="0.15"/>
    </linearGradient>`;
    svg.appendChild(defs);
    
    function createSvg(tag, attrs) {{
      const el = document.createElementNS("http://www.w3.org/2000/svg", tag);
      for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v);
      return el;
    }}
    
    let bandStart = 0;
    for (let i = 1; i <= coords.length; i++) {{
      if (i === coords.length || coords[i].dayIdx !== coords[bandStart].dayIdx) {{
        const x1 = bandStart === 0 ? 0 : (coords[bandStart - 1].x + coords[bandStart].x) / 2;
        const x2 = i === coords.length ? svgWidth : (coords[i - 1].x + coords[i].x) / 2;
        
        if (bandStart > 0) {{
          svg.appendChild(createSvg("line", {{ x1: x1, y1: 0, x2: x1, y2: 185 - padBottom, stroke: "{grid_color}", "stroke-width": "1.5", "stroke-dasharray": "4,4" }}));
        }}
        
        const midX = (x1 + x2) / 2;
        const dayLabel = createSvg("text", {{ x: midX, y: padTop - 10, fill: "{text_color}", "font-size": "11", "font-weight": "800", "text-anchor": "middle" }});
        dayLabel.textContent = coords[bandStart].day;
        svg.appendChild(dayLabel);
        
        bandStart = i;
      }}
    }}
    
    const lineCoords = coords.filter(c => !c.isGap);
    let pathD = "";
    lineCoords.forEach((c, idx) => {{
        if (idx === 0) pathD += `M ${{c.x}} ${{c.y}}`;
        else {{
            const prev = lineCoords[idx - 1]; const cpX = (prev.x + c.x) / 2;
            pathD += ` C ${{cpX}} ${{prev.y}}, ${{cpX}} ${{c.y}}, ${{c.x}} ${{c.y}}`;
        }}
    }});
    
    const plotHeight = 185 - padTop - padBottom;
    if (lineCoords.length > 0) {{
      const fillD = pathD + ` L ${{lineCoords[lineCoords.length-1].x}} ${{padTop + plotHeight}} L ${{lineCoords[0].x}} ${{padTop + plotHeight}} Z`;
      svg.appendChild(createSvg("path", {{ d: fillD, fill: "url(#waveGrad)" }}));
      svg.appendChild(createSvg("path", {{ d: pathD, fill: "none", stroke: "{chart_line}", "stroke-width": "3", "stroke-linecap": "round" }}));
    }}
    
    coords.forEach(c => {{
      if (!c.isGap && c.isMarkedHour) {{
        svg.appendChild(createSvg("circle", {{ cx: c.x, cy: c.y, r: "4.5", fill: "{card_bg}", stroke: c.ratingColor, "stroke-width": "2.5" }}));
        
        const waveLabel = createSvg("text", {{ x: c.x, y: c.y - 10, fill: "{text_color}", "font-size": "9", "font-weight": "800", "text-anchor": "middle" }});
        waveLabel.textContent = c.wave.replace(' ', '');
        svg.appendChild(waveLabel);

        const timeLabel = createSvg("text", {{ x: c.x, y: padTop + plotHeight + 18, fill: "{sub_text}", "font-size": "10", "font-weight": "700", "text-anchor": "middle" }});
        timeLabel.textContent = c.time.split(" ")[1];
        svg.appendChild(timeLabel);
      }}
    }});
    
    const scrubLine = createSvg("line", {{x1: 0, y1: 0, x2: 0, y2: padTop + plotHeight, stroke: "{text_color}", "stroke-width": "1.5", "stroke-dasharray": "3,2", opacity: "0"}});
    const activeDot = createSvg("circle", {{cx: 0, cy: 0, r: "5.5", fill: "{card_bg}", stroke: "{text_color}", "stroke-width": "2.5", opacity: "0"}});
    svg.appendChild(scrubLine); svg.appendChild(activeDot);
    
    const scrollArea = document.getElementById("scrollArea");
    const dataBox = document.getElementById("dataBox");
    let selectedIdx = null;
    let isBoxVisible = false;
    
    function showData(idx) {{
      selectedIdx = idx; const c = lineCoords[idx];
      if (!c) return;
      scrubLine.setAttribute("x1", c.x); scrubLine.setAttribute("x2", c.x); scrubLine.setAttribute("opacity", "0.5");
      activeDot.setAttribute("cx", c.x); activeDot.setAttribute("cy", c.y); activeDot.setAttribute("opacity", "1");
      
      dataBox.innerHTML = `
        <div class="db-header">
            <span>${{c.time}}</span><span style="color:${{c.ratingColor}}">${{c.rating}}</span><span class="close-btn" onclick="hideData()">✕</span>
        </div>
        <div class="db-grid">
            <div class="db-cell">Wave <span class="db-val">${{c.wave}}</span></div>
            <div class="db-cell">Wind <span class="db-val">${{c.windSpeed}}</span></div>
        </div>
      `;
      isBoxVisible = true; dataBox.classList.add("visible"); 
    }}
    
    window.hideData = function() {{ 
        isBoxVisible = false; dataBox.classList.remove("visible"); 
        scrubLine.setAttribute("opacity", "0"); activeDot.setAttribute("opacity", "0"); 
    }};

    let isDragging = false;
    let startX = 0, startY = 0;
    let longPressTimer = null;

    scrollArea.addEventListener("touchstart", (e) => {{
        if(e.touches.length !== 1) return;
        startX = e.touches.length > 0 ? e.touches[0].clientX : 0;
        startY = e.touches.length > 0 ? e.touches[0].clientY : 0;
        isDragging = false;

        if (isBoxVisible) {{
            const relX = startX - svg.getBoundingClientRect().left;
            const currentScrubX = parseFloat(scrubLine.getAttribute("x1"));
            
            if (Math.abs(relX - currentScrubX) < 40) {{
                longPressTimer = setTimeout(() => {{
                    isDragging = true;
                    if(navigator.vibrate) navigator.vibrate(20);
                }}, 250);
            }}
        }}
    }}, {{passive: true}});

    scrollArea.addEventListener("touchmove", (e) => {{
        if(e.touches.length !== 1) return;
        
        if (!isDragging) {{
            const dx = Math.abs(e.touches[0].clientX - startX);
            const dy = Math.abs(e.touches[0].clientY - startY);
            if (dx > 10 || dy > 10) clearTimeout(longPressTimer);
            return;
        }}
        
        e.preventDefault();
        const relX = e.touches[0].clientX - svg.getBoundingClientRect().left;
        let closestIdx = 0;
        let minDst = Infinity;
        lineCoords.forEach((lc, lci) => {{
            const dst = Math.abs(lc.x - relX);
            if (dst < minDst) {{ minDst = dst; closestIdx = lci; }}
        }});
        if (selectedIdx !== closestIdx) showData(closestIdx);
    }}, {{passive: false}});

    scrollArea.addEventListener("touchend", () => {{
        clearTimeout(longPressTimer);
        setTimeout(() => {{ isDragging = false; }}, 50);
    }}, {{passive: true}});

    scrollArea.addEventListener("click", (e) => {{
        if (isDragging) return; 
        const relX = e.clientX - svg.getBoundingClientRect().left;
        let closestIdx = 0;
        let minDst = Infinity;
        lineCoords.forEach((lc, lci) => {{
            const dst = Math.abs(lc.x - relX);
            if (dst < minDst) {{ minDst = dst; closestIdx = lci; }}
        }});
        if (isBoxVisible && closestIdx === selectedIdx) hideData(); else showData(closestIdx);
    }});
  </script>
</body>
</html>
"""
components.html(html_chart, height=360)


# --- HTML Table Generation (Surfline Style) ---
def generate_html_rows(day_df, u_sys):
    html = ""
    for _, row in day_df.iterrows():
        time_str = row["HourStr"]
        
        wv_m = row["Wave Height (m)"]
        if pd.isna(wv_m):
            wv_color = text_color
            surf_str = "Flat"
        else:
            if wv_m <= 0.6:
                wv_color = "#DC2626" if not is_dark else "#EF4444"
            elif wv_m <= 0.9:
                wv_color = "#D97706" if not is_dark else "#F59E0B"
            else:
                wv_color = "#16A34A" if not is_dark else "#22C55E"
            
            if u_sys == "metric":
                if wv_m < 1.0:
                    display_text = f"{int(round(wv_m * 100))}cm"
                else:
                    display_text = f"{wv_m:.1f}m"
            else:
                display_text = f"{round(wv_m * 3.28084, 1)}ft"
                
            surf_str = f"<span class='sf-val-main' style='color: {wv_color}; font-size: 0.95rem; white-space: nowrap;'>{display_text}</span>"
            
        rt_txt, rt_col, rt_bg = get_rating_details(row["Score"], is_dark)
        
        sw_m = row["Swell (m)"]
        sw_p = row["Period (s)"]
        
        if pd.isna(sw_m):
            swell_str = "-"
        else:
            if u_sys == "metric":
                if sw_m < 1.0:
                    sw_display = f"{int(round(sw_m * 100))}cm"
                else:
                    sw_display = f"{sw_m:.1f}m"
            else:
                sw_display = f"{round(sw_m * 3.28084, 1)}ft"
                
            swell_str = f"<span class='sf-val-main' style='font-size: 0.95rem; white-space: nowrap;'>{sw_display}</span> <span class='sf-val-sub'>{sw_p:.0f}s</span>"
        
        w_spd = row["Wind Speed (km/h)"]
        w_dir = row["Wind Direction (°)"]
        wind_spd_str = f"{w_spd:.0f} <span class='sf-val-sub'>kph</span>" if not pd.isna(w_spd) else "-"
        arrow_deg = w_dir if not pd.isna(w_dir) else 0

        air_t = row["Air Temp (°C)"]
        air_str = f"{air_t:.0f}°" if not pd.isna(air_t) else "-"
        w_code = row["Weather Code"]
        w_icon = get_weather_icon(w_code)

        wat_t = row["Water Temp (°C)"]
        wat_str = f"💧 {wat_t:.1f}°" if not pd.isna(wat_t) else "-"

        uv_val = row["UV Index"]
        if pd.isna(uv_val):
            uv_html = "-"
        else:
            uv_color = "#22C55E" if uv_val < 3 else ("#F59E0B" if uv_val < 6 else ("#EF4444" if uv_val < 8 else "#B91C1C"))
            uv_html = f'<span class="sf-val-main" style="color: {uv_color}; font-size: 0.95rem;">{uv_val:.0f}</span><br><span class="sf-val-sub">UV</span>'

        html += f'<div class="sf-row"><div class="sf-time">{time_str}</div><div class="sf-col">{surf_str}<br><div class="rating-badge" style="color: {rt_col}; background: {rt_bg};">{rt_txt}</div></div><div class="sf-col">{swell_str}</div><div class="sf-col"><div class="wind-arrow-container"><span class="sf-val-main">{wind_spd_str}</span><span class="wind-arrow" style="transform: rotate({arrow_deg}deg); display: inline-block;">↓</span></div></div><div class="sf-col sf-val-main" style="font-size: 1rem;">{w_icon} {air_str}</div><div class="sf-col sf-val-main">{wat_str}</div><div class="sf-col">{uv_html}</div></div>'
    return html


# Only look at daylight hours for tables
# Only look at daylight hours for tables (Guaranteed to show at least 06:00 to 18:00)
df_daylight = df[
    ((df["DateTime"] >= (df["Sunrise"] - pd.Timedelta(minutes=30))) & 
     (df["DateTime"] <= (df["Sunset"] + pd.Timedelta(minutes=30)))) |
    ((df["DateTime"].dt.hour >= 6) & (df["DateTime"].dt.hour <= 18))
].copy()

# Inject Dynamic CSS to perfectly color our matched Left/Right unit buttons
is_metric = (unit_sys == "metric")
st.markdown(f"""
<style>
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {{
    background-color: {"" + active_bg + "" if is_metric else "" + inactive_bg + ""} !important;
    color: {"" + active_fg + "" if is_metric else "" + inactive_fg + ""} !important;
}}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) button p {{
    color: {"" + active_fg + "" if is_metric else "" + inactive_fg + ""} !important;
}}

div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {{
    background-color: {"" + active_bg + "" if not is_metric else "" + inactive_bg + ""} !important;
    color: {"" + active_fg + "" if not is_metric else "" + inactive_fg + ""} !important;
}}
div[data-testid="stHorizontalBlock"] > div:nth-child(2) button p {{
    color: {"" + active_fg + "" if not is_metric else "" + inactive_fg + ""} !important;
}}
</style>
""", unsafe_allow_html=True)

# Render Unit Buttons (Left & Right evenly)
col_cm, col_ft = st.columns(2)

with col_cm:
    if st.button("cm", use_container_width=True):
        if unit_sys != "metric":
            st.session_state.unit = "metric"
            st.rerun()

with col_ft:
    if st.button("ft", use_container_width=True):
        if unit_sys != "imperial":
            st.session_state.unit = "imperial"
            st.rerun()


# Render Days
for i, d in enumerate(unique_dates):
    day_dl_df = df_daylight[df_daylight["Date"] == d].copy()
    if day_dl_df.empty: continue

    day_ts = pd.Timestamp(d)
    if i == 0: day_title = f"Today, {day_ts.strftime('%m/%d')}"
    elif i == 1: day_title = f"Tomorrow, {day_ts.strftime('%m/%d')}"
    else: day_title = day_ts.strftime("%A, %m/%d")

    st.markdown(f'<div class="day-header">{day_title}</div>', unsafe_allow_html=True)
    
    # Create Summary Data (Morning, Noon, Evening)
    # Create Summary Data (Morning, Noon, Evening) - הותאם ל-6, 12, 18
    summary_hours = []
    for label, target_h in [("Morning", 6), ("Noon", 12), ("Evening", 18)]:
        subset = day_dl_df.iloc[(day_dl_df['DateTime'].dt.hour - target_h).abs().argsort()[:1]]
        if not subset.empty:
            row = subset.iloc[0].copy()
            row["HourStr"] = label
            summary_hours.append(row)
    
    summary_df = pd.DataFrame(summary_hours)
    
    # Render Summary Table
    if not summary_df.empty:
        summary_html = f'<div class="sf-table-wrapper"><div class="sf-table-container"><div class="sf-header-row"><div></div><div>Surf</div><div>Swell</div><div>Wind</div><div>Weather</div><div>Water</div><div>UV</div></div>{generate_html_rows(summary_df, unit_sys)}</div></div>'
        st.markdown(summary_html, unsafe_allow_html=True)

    # Hourly Expander - סינון מ-6 בבוקר ובקפיצות של 3 שעות
    with st.expander("Show all daylight hours"):
        expander_df = day_dl_df[(day_dl_df['DateTime'].dt.hour >= 6) & (day_dl_df['DateTime'].dt.hour % 3 == 0)]
        hourly_html = f'<div class="sf-table-wrapper" style="box-shadow: none; border: none; margin-bottom: 0;"><div class="sf-table-container"><div class="sf-header-row" style="border-top-left-radius: 12px; border-top-right-radius: 12px;"><div></div><div>Surf</div><div>Swell</div><div>Wind</div><div>Weather</div><div>Water</div><div>UV</div></div>{generate_html_rows(expander_df, unit_sys)}</div></div>'
        st.markdown(hourly_html, unsafe_allow_html=True)
