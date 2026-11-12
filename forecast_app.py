import json
import streamlit as st
import streamlit.components.v1 as components
import requests
import pandas as pd

st.set_page_config(page_title="Surf & Wind Forecast", page_icon="🌊", layout="wide")

# Minimal Coastal Theme CSS Override
st.markdown(
    """
    <style>
    /* Force Light Coastal Background */
    .stApp, .stApp > header {
        background-color: #F7F5F0 !important;
    }
    .block-container {
        padding-top: 2rem !important;
    }
    /* Prevent horizontal page overflow on mobile */
    .stApp {
        overflow-x: clip !important;
    }
    [data-testid="stMainBlockContainer"], .block-container,
    [data-testid="stVerticalBlock"], [data-testid="stElementContainer"] {
        min-width: 0 !important;
        max-width: 100% !important;
    }
    h1, h2, h3, p, span {
        color: #2C3E50 !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }
    .compact-row {
        display: flex;
        gap: 10px;
        width: 100%;
        margin-bottom: 12px;
    }
    /* Clean, white, flat cards */
    .cam-btn, .stat-card, .day-header {
        background-color: #FFFFFF !important;
        border: 1px solid #E8E5DF !important;
        border-radius: 12px !important;
        color: #2C3E50 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important;
    }
    .cam-btn {
        flex: 1;
        text-align: center;
        padding: 10px 6px;
        text-decoration: none !important;
        font-size: 0.85rem;
        font-weight: 600;
        transition: 0.2s;
    }
    .cam-btn:active {
        background-color: #F0F2F6 !important;
    }
    .stat-card {
        flex: 1;
        padding: 10px 6px;
        text-align: center;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #7F8C8D !important;
        margin-bottom: 2px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .stat-value {
        font-size: 1.2rem;
        font-weight: 700;
        line-height: 1.2;
    }
    .stat-sub {
        font-size: 0.7rem;
        margin-top: 3px;
        color: #95A5A6 !important;
    }
    .day-header {
        margin-top: 18px;
        margin-bottom: 8px;
        padding: 8px 12px;
        font-weight: 700;
        font-size: 1.05rem;
        border-left: 5px solid #3498DB !important;
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

# 2. Side-by-side Live Cam Buttons
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
        return f"{temp:.1f}°C", "Boardshorts 🩳"
    elif temp >= 23.0:
        return f"{temp:.1f}°C", "Spring / 2mm 👕"
    elif temp >= 20.0:
        return f"{temp:.1f}°C", "3/2mm Suit 🩱"
    else:
        return f"{temp:.1f}°C", "4/3mm Suit 🥶"


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


def get_rating_tier(score):
    if score >= 7.0:
        return "🟢"
    elif score >= 4.0:
        return "🟠"
    return "🔴"


def format_rating_badge(score):
    dot = get_rating_tier(score)
    return f"{score}/10 {dot}"


def get_full_table_height(num_rows):
    return (num_rows + 1) * 35 + 8


def build_day_period_summary(day_df):
    periods = [
        ("🌅 Morning", 6, 10),
        ("☀️ Noon", 11, 14),
        ("🌇 Evening", 15, 19),
    ]
    summary_rows = []
    for label, start_h, end_h in periods:
        subset = day_df[day_df["DateTime"].dt.hour.between(start_h, end_h)]
        if subset.empty:
            continue
        best_idx = subset["Score"].idxmax()
        rep_row = subset.loc[best_idx].copy()
        rep_row["Session"] = label
        summary_rows.append(rep_row)

    if not summary_rows:
        return pd.DataFrame()
    return pd.DataFrame(summary_rows)


def render_touch_scrub_chart(df, max_wave):
    points_data = []
    for _, row in df.iterrows():
        val = row["Wave Height (m)"]
        points_data.append({
            "time": row["Time"],
            "day": row["Day"],
            "dayIdx": int(row["DayIdx"]),
            "hour": int(row["DateTime"].hour),
            "rating": row["Rating"],
            "wave": row["Wave Height"],
            "waveRaw": 0.0 if pd.isna(val) else float(val),
            "swell": row["Swell"],
            "period": row["Period"],
            "windType": row["Wind Type"],
            "windSpeed": row["Wind Speed"],
        })

    y_top_label = format_height_with_unit(max_wave)
    y_mid_label = format_height_with_unit(max_wave / 2.0)

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
      * {{
        box-sizing: border-box;
        -webkit-user-select: none;
        user-select: none;
        -webkit-touch-callout: none;
        -webkit-tap-highlight-color: transparent;
      }}
      html, body {{
        margin: 0;
        padding: 0;
        background: transparent;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #2C3E50;
        overflow: hidden;
      }}
      /* Minimal Coastal Chart Styling */
      .chart-card {{
        background: #FFFFFF;
        border: 1px solid #E8E5DF;
        border-radius: 12px;
        padding: 12px 8px 8px 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
      }}
      .top-bar {{
        display: flex;
        justify-content: flex-end;
        margin-bottom: 8px;
        padding: 0 4px;
      }}
      .hint-badge {{
        font-size: 11px;
        padding: 3px 10px;
        border-radius: 999px;
        background: #F7F5F0;
        color: #7F8C8D;
        transition: all 0.15s ease;
      }}
      .hint-badge.active {{
        background: #E8F4FD;
        color: #3498DB;
        font-weight: 600;
      }}
      .data-box {{
        display: none;
        width: 100%;
        margin-bottom: 12px;
        background: #FFFFFF;
        border: 1px solid #E8E5DF;
        border-radius: 10px;
        padding: 10px 12px;
        font-size: 12px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.04);
      }}
      .data-box.visible {{
        display: block;
      }}
      .db-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 700;
        font-size: 13px;
        border-bottom: 1px solid #F0F2F6;
        padding-bottom: 6px;
        margin-bottom: 8px;
        color: #2C3E50;
      }}
      .db-close {{
        font-size: 14px;
        color: #BDC3C7;
      }}
      .db-grid {{
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 8px;
        text-align: center;
      }}
      .db-cell {{
        background: #F9F8F6;
        border-radius: 6px;
        padding: 6px 4px;
      }}
      .db-lbl {{
        display: block;
        font-size: 10px;
        color: #7F8C8D;
        text-transform: uppercase;
        margin-bottom: 2px;
      }}
      .db-val {{
        font-weight: 700;
        font-size: 12px;
        color: #2C3E50;
      }}
      .chart-shell {{
        display: flex;
        position: relative;
        width: 100%;
        height: 270px;
      }}
      .y-axis {{
        width: 65px;
        flex-shrink: 0;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 16px 6px 46px 0;
        text-align: right;
        font-size: 9.5px;
        color: #95A5A6;
      }}
      .scroll-area {{
        flex: 1;
        overflow-x: auto;
        overflow-y: hidden;
        -webkit-overflow-scrolling: touch;
        touch-action: pan-x pan-y;
        position: relative;
        cursor: pointer;
        border-left: 1px solid #F0F2F6;
      }}
      .scroll-area.scrubbing {{
        overflow-x: hidden !important;
        touch-action: none !important;
      }}
    </style>
    </head>
    <body oncontextmenu="return false;">
      <div class="chart-card" id="chartCard">
        <div class="top-bar">
          <div class="hint-badge" id="hintBadge">Tap • Hold to drag</div>
        </div>
        <div class="data-box" id="dataBox"></div>
        <div class="chart-shell">
          <div class="y-axis">
            <span>{y_top_label}</span>
            <span>{y_mid_label}</span>
            <span>0 cm</span>
          </div>
          <div class="scroll-area" id="scrollArea">
            <svg id="waveSvg" height="270"></svg>
          </div>
        </div>
      </div>

      <script>
        const points = {json.dumps(points_data)};
        const maxWave = {max_wave};

        // Minimal layout: 06:00 to 17:00
        const stepX = 28;
        const padLeft = 18;
        const padRight = 22;
        const padTop = 18;
        const padBottom = 48;
        const plotHeight = 270 - padTop - padBottom;
        const svgWidth = Math.max(600, padLeft + padRight + (points.length - 1) * stepX);

        const svg = document.getElementById("waveSvg");
        svg.setAttribute("width", svgWidth);
        const svgNS = "http://www.w3.org/2000/svg";

        function createSvgEl(tag, attrs) {{
          const el = document.createElementNS(svgNS, tag);
          for (const [k, v] of Object.entries(attrs)) {{
            el.setAttribute(k, v);
          }}
          return el;
        }}

        const coords = points.map((p, i) => {{
          const x = padLeft + i * stepX;
          const ratio = Math.min(1, Math.max(0, p.waveRaw / maxWave));
          const y = padTop + plotHeight * (1 - ratio);
          return {{ ...p, x, y, idx: i }};
        }});

        // Draw clean vertical day separators instead of heavy background colors
        let bandStart = 0;
        for (let i = 1; i <= coords.length; i++) {{
          if (i === coords.length || coords[i].dayIdx !== coords[bandStart].dayIdx) {{
            const x1 = bandStart === 0 ? 0 : (coords[bandStart - 1].x + coords[bandStart].x) / 2;
            if (bandStart > 0) {{
              svg.appendChild(createSvgEl("line", {{
                x1: x1, y1: padTop, x2: x1, y2: padTop + plotHeight,
                stroke: "#E8E5DF",
                "stroke-width": "1.5",
                "stroke-dasharray": "4,4"
              }}));
            }}
            bandStart = i;
          }}
        }}

        // Clean subtle grid lines
        [0, 0.5, 1].forEach(frac => {{
          const gy = padTop + plotHeight * (1 - frac);
          svg.appendChild(createSvgEl("line", {{
            x1: 0, y1: gy, x2: svgWidth, y2: gy,
            stroke: "rgba(0,0,0,0.04)",
            "stroke-dasharray": frac === 0 ? "none" : "3,3"
          }}));
        }});

        // Minimal Wave Path (Navy Blue)
        if (coords.length > 0) {{
          const pathD = coords.map((c, idx) => `${{idx === 0 ? "M" : "L"}} ${{c.x}} ${{c.y}}`).join(" ");
          svg.appendChild(createSvgEl("path", {{
            d: pathD,
            fill: "none",
            stroke: "#2C3E50",
            "stroke-width": "2.8",
            "stroke-linejoin": "round",
            "stroke-linecap": "round"
          }}));
        }}

        // Simple single-color dots for data points
        const mainColor = "#3498DB";
        coords.forEach((c) => {{
          const isKeyHour = (c.hour === 6 || c.hour === 12 || c.hour === 17);
          svg.appendChild(createSvgEl("circle", {{
            cx: c.x,
            cy: c.y,
            r: isKeyHour ? "4.5" : "3.0",
            fill: mainColor,
            stroke: "#FFF",
            "stroke-width": isKeyHour ? "1.5" : "0"
          }}));

          if (isKeyHour) {{
            svg.appendChild(createSvgEl("line", {{
              x1: c.x, y1: padTop + plotHeight, x2: c.x, y2: padTop + plotHeight + 6,
              stroke: "#BDC3C7"
            }}));
            const label = createSvgEl("text", {{
              x: c.x,
              y: padTop + plotHeight + 16,
              fill: "#7F8C8D",
              "font-size": "10",
              "font-weight": "500",
              "text-anchor": "end",
              transform: `rotate(-35 ${{c.x}} ${{padTop + plotHeight + 16}})`
            }});
            label.textContent = c.time;
            svg.appendChild(label);
          }}
        }});

        const scrubLine = createSvgEl("line", {{
          x1: 0, y1: padTop, x2: 0, y2: padTop + plotHeight,
          stroke: "#3498DB",
          "stroke-width": "2",
          "stroke-dasharray": "4,3",
          opacity: "0"
        }});
        svg.appendChild(scrubLine);

        const activeHalo = createSvgEl("circle", {{
          cx: 0, cy: 0, r: "11",
          fill: "rgba(52, 152, 219, 0.15)",
          opacity: "0"
        }});
        svg.appendChild(activeHalo);

        const activeDot = createSvgEl("circle", {{
          cx: 0, cy: 0, r: "5.5",
          fill: "#FFFFFF",
          stroke: "#3498DB",
          "stroke-width": "2.5",
          opacity: "0"
        }});
        svg.appendChild(activeDot);

        const chartCard = document.getElementById("chartCard");
        const scrollArea = document.getElementById("scrollArea");
        const dataBox = document.getElementById("dataBox");
        const hintBadge = document.getElementById("hintBadge");

        let selectedIdx = null;
        let isBoxVisible = false;
        let isScrubbing = false;
        let ignoreNextClick = false;
        let longPressTimer = null;
        let stopTimer = null;
        let touchStartX = 0;
        let touchStartY = 0;

        function syncIframeHeight() {{
          try {{
            if (window.frameElement) {{
              window.frameElement.style.height = (chartCard.offsetHeight + 6) + "px";
            }}
          }} catch (e) {{}}
        }}

        function getNearestIndex(clientX) {{
          const rect = svg.getBoundingClientRect();
          const relX = clientX - rect.left;
          const rawIdx = Math.round((relX - padLeft) / stepX);
          return Math.min(coords.length - 1, Math.max(0, rawIdx));
        }}

        function moveCursorTo(idx) {{
          selectedIdx = idx;
          const c = coords[idx];
          scrubLine.setAttribute("x1", c.x);
          scrubLine.setAttribute("x2", c.x);
          scrubLine.setAttribute("opacity", "0.8");

          activeHalo.setAttribute("cx", c.x);
          activeHalo.setAttribute("cy", c.y);
          activeHalo.setAttribute("opacity", "1");

          activeDot.setAttribute("cx", c.x);
          activeDot.setAttribute("cy", c.y);
          activeDot.setAttribute("opacity", "1");
        }}

        function hideDataBoxOnly() {{
          isBoxVisible = false;
          dataBox.classList.remove("visible");
          syncIframeHeight();
        }}

        function closeAllSelection() {{
          selectedIdx = null;
          isBoxVisible = false;
          dataBox.classList.remove("visible");
          scrubLine.setAttribute("opacity", "0");
          activeHalo.setAttribute("opacity", "0");
          activeDot.setAttribute("opacity", "0");
          syncIframeHeight();
        }}

        function showDataBox() {{
          if (selectedIdx === null) return;
          const c = coords[selectedIdx];

          dataBox.innerHTML = `
            <div class="db-header">
              <span>${{c.time}}</span>
              <span>${{c.rating}}</span>
              <span class="db-close">✕</span>
            </div>
            <div class="db-grid">
              <div class="db-cell"><span class="db-lbl">Wave</span><span class="db-val">${{c.wave}}</span></div>
              <div class="db-cell"><span class="db-lbl">Swell</span><span class="db-val">${{c.swell}}</span></div>
              <div class="db-cell"><span class="db-lbl">Period</span><span class="db-val">${{c.period}}</span></div>
              <div class="db-cell"><span class="db-lbl">Wind</span><span class="db-val">${{c.windType}}</span></div>
              <div class="db-cell"><span class="db-lbl">Speed</span><span class="db-val">${{c.windSpeed}}</span></div>
            </div>
          `;

          isBoxVisible = true;
          dataBox.classList.add("visible");
          syncIframeHeight();
        }}

        dataBox.addEventListener("click", (e) => {{
          e.stopPropagation();
          closeAllSelection();
        }});

        scrollArea.addEventListener("click", (e) => {{
          if (ignoreNextClick) {{
            ignoreNextClick = false;
            return;
          }}
          const idx = getNearestIndex(e.clientX);
          if (isBoxVisible && idx === selectedIdx) {{
            closeAllSelection();
          }} else {{
            moveCursorTo(idx);
            showDataBox();
          }}
        }});

        scrollArea.addEventListener("touchstart", (e) => {{
          if (e.touches.length !== 1) return;
          const t = e.touches[0];
          touchStartX = t.clientX;
          touchStartY = t.clientY;

          clearTimeout(longPressTimer);
          clearTimeout(stopTimer);

          longPressTimer = setTimeout(() => {{
            isScrubbing = true;
            ignoreNextClick = true;
            scrollArea.classList.add("scrubbing");
            hintBadge.textContent = "Drag bar • Stop to view";
            hintBadge.classList.add("active");
            if (navigator.vibrate) navigator.vibrate(25);

            const idx = getNearestIndex(touchStartX);
            moveCursorTo(idx);
            hideDataBoxOnly();
          }}, 260);
        }}, {{ passive: true }});

        scrollArea.addEventListener("touchmove", (e) => {{
          if (e.touches.length !== 1) return;
          const t = e.touches[0];

          if (!isScrubbing) {{
            const dx = Math.abs(t.clientX - touchStartX);
            const dy = Math.abs(t.clientY - touchStartY);
            if (dx > 10 || dy > 10) {{
              clearTimeout(longPressTimer);
            }}
            return;
          }}

          e.preventDefault();
          const idx = getNearestIndex(t.clientX);
          if (idx !== selectedIdx) {{
            moveCursorTo(idx);
          }}
          hideDataBoxOnly();

          clearTimeout(stopTimer);
          stopTimer = setTimeout(() => {{
            showDataBox();
          }}, 220);
        }}, {{ passive: false }});

        function endTouch() {{
          clearTimeout(longPressTimer);
          clearTimeout(stopTimer);

          if (isScrubbing) {{
            isScrubbing = false;
            scrollArea.classList.remove("scrubbing");
            hintBadge.textContent = "Tap • Hold to drag";
            hintBadge.classList.remove("active");
            showDataBox();
            setTimeout(() => {{ ignoreNextClick = false; }}, 350);
          }}
        }}

        scrollArea.addEventListener("touchend", endTouch, {{ passive: true }});
        scrollArea.addEventListener("touchcancel", endTouch, {{ passive: true }});

        let mouseDown = false;
        let mouseDragged = false;
        let mouseDownX = 0;

        svg.addEventListener("mousedown", (e) => {{
          mouseDown = true;
          mouseDragged = false;
          mouseDownX = e.clientX;
        }});
        window.addEventListener("mousemove", (e) => {{
          if (!mouseDown) return;
          if (Math.abs(e.clientX - mouseDownX) > 5) {{
            mouseDragged = true;
            ignoreNextClick = true;
          }}
          if (!mouseDragged) return;
          const idx = getNearestIndex(e.clientX);
          moveCursorTo(idx);
          hideDataBoxOnly();
          clearTimeout(stopTimer);
          stopTimer = setTimeout(() => showDataBox(), 180);
        }});
        window.addEventListener("mouseup", () => {{
          if (!mouseDown) return;
          mouseDown = false;
          clearTimeout(stopTimer);
          if (mouseDragged) {{
            showDataBox();
            setTimeout(() => {{ ignoreNextClick = false; }}, 100);
          }}
        }});

        syncIframeHeight();
      </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)


# Load spot forecast
df, daily_df, water_temp = get_forecast_data(spot["lat"], spot["lon"])

unique_dates = sorted(df["Date"].unique())
day_to_idx = {d: i for i, d in enumerate(unique_dates)}
df["DayIdx"] = df["Date"].map(day_to_idx)

# 3. Side-by-side Water Temp, Sunrise & Sunset Cards
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

# Classify wind, compute rating, and format display columns with units
df["Wind Type"] = df["Wind Direction (°)"].apply(
    lambda d: get_wind_type(d, spot["offshore"], spot["onshore"])
)
df["Score"] = df.apply(
    lambda r: calculate_surf_rating(r, spot["offshore"], spot["onshore"]), axis=1
)
df["Rating"] = df["Score"].apply(format_rating_badge)
df["Wave Height"] = df["Wave Height (m)"].apply(format_height_with_unit)
df["Swell"] = df["Swell (m)"].apply(format_height_with_unit)
df["Period"] = df["Period (s)"].apply(format_period_with_unit)
df["Wind Speed"] = df["Wind Speed (km/h)"].apply(format_wind_with_unit)

# 4. Dynamic Daylight Filter
df = df.merge(daily_df, on="Date", how="left")
df_daylight = df[
    (df["DateTime"] >= (df["Sunrise"] - pd.Timedelta(minutes=30)))
    & (df["DateTime"] <= (df["Sunset"] + pd.Timedelta(minutes=30)))
].copy()

# 5. Session Recommendations (Top Green Tier >= 7.0)
best_conditions = df_daylight[df_daylight["Score"] >= 7.0]

st.subheader("🏄 Session Recommendations")
if not best_conditions.empty:
    st.success(
        f"Prime windows spotted at {selected_spot_name}! Clean wall and favorable winds for pumping and rail carves:"
    )
    rec_cols = ["Time", "Rating", "Wave Height", "Period", "Wind Type", "Wind Speed"]
    # Clean, plain Streamlit dataframe without background colors
    st.dataframe(best_conditions[rec_cols], hide_index=True, height=get_full_table_height(len(best_conditions)))
elif df_daylight["Wave Height (m)"].max() < 0.45:
    st.warning("Flat spell ahead. Ideal time for a dry-land surfskate session to dial in foot placement and carving mechanics.")
else:
    st.info("No green-tier (7.0+) sessions this week — check the daily Morning / Noon / Evening breakdowns below.")

# 6. Interactive 7-Day Wave Height Chart (Daytime hours 06:00 - 17:00)
st.subheader("Wave Height Chart (06:00–17:00)")
df_chart = df[df["DateTime"].dt.hour.between(6, 17)].copy()
max_wave = float(df_chart["Wave Height (m)"].max())
if pd.isna(max_wave) or max_wave <= 0:
    max_wave = 1.0

render_touch_scrub_chart(df_chart, max_wave)

# 7. Per-Day Forecast Tables (Morning / Noon / Evening + Expandable Hourly Breakdown)
st.subheader("Daily Forecast")
summary_cols = ["Session", "Rating", "Wave Height", "Swell", "Period", "Wind Type", "Wind Speed"]
hourly_cols = ["HourStr", "Rating", "Wave Height", "Swell", "Period", "Wind Type", "Wind Speed"]

for i, d in enumerate(unique_dates):
    day_full_df = df[df["Date"] == d].copy()
    day_dl_df = df_daylight[df_daylight["Date"] == d].copy()

    day_ts = pd.Timestamp(d)
    if i == 0:
        day_title = f"Today — {day_ts.strftime('%A (%d/%m)')}"
    elif i == 1:
        day_title = f"Tomorrow — {day_ts.strftime('%A (%d/%m)')}"
    else:
        day_title = day_ts.strftime("%A (%d/%m)")

    st.markdown(f'<div class="day-header">{day_title}</div>', unsafe_allow_html=True)

    summary_df = build_day_period_summary(day_full_df)
    if not summary_df.empty:
        # Clean plain dataframe
        st.dataframe(summary_df[summary_cols], hide_index=True, height=get_full_table_height(len(summary_df)))

    with st.expander(f"All Daylight Hours — {day_ts.strftime('%A')}"):
        clean_hourly_df = day_dl_df[hourly_cols].rename(columns={"HourStr": "Hour"})
        st.dataframe(clean_hourly_df, hide_index=True, height=get_full_table_height(len(day_dl_df)))
