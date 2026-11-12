import streamlit as st
import requests
import pandas as pd

# קואורדינטות של קו החוף באזור המרכז
LATITUDE = 32.08
LONGITUDE = 34.78

st.set_page_config(page_title="תחזית גלים ורוח", layout="wide")
st.title("🌊 תחזית גלים ורוח - 3 ימים קדימה")

@st.cache_data
def get_forecast_data():
    # פנייה ל-API של הים למשיכת גובה גל וזמן מחזור
    marine_url = f"https://marine-api.open-meteo.com/v1/marine?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=wave_height,wave_period&timezone=auto&forecast_days=3"
    wave_data = requests.get(marine_url).json()
    
    # פנייה ל-API של מזג האוויר למשיכת מהירות וכיוון רוח
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&hourly=wind_speed_10m,wind_direction_10m&timezone=auto&forecast_days=3"
    wind_data = requests.get(weather_url).json()
    
    # איחוד הנתונים לטבלה מסודרת
    df = pd.DataFrame({
        "זמן": wave_data["hourly"]["time"],
        "גובה גל (מ)": wave_data["hourly"]["wave_height"],
        "זמן מחזור (שניות)": wave_data["hourly"]["wave_period"],
        "מהירות רוח (קמש)": wind_data["hourly"]["wind_speed_10m"],
        "כיוון רוח (מעלות)": wind_data["hourly"]["wind_direction_10m"]
    })
    
    # עיצוב התאריך והשעה לפורמט קריא
    df["זמן"] = pd.to_datetime(df["זמן"]).dt.strftime("%d/%m %H:00")
    return df

def get_wind_type(direction):
    if pd.isna(direction):
        return ""
    if 45 <= direction <= 135:
        return "אוף-שור 💨"
    elif 225 <= direction <= 315:
        return "און-שור 🌊"
    else:
        return "קרוס-שור"

# משיכת הנתונים והוספת עמודת סוג הרוח
df = get_forecast_data()
df["סוג רוח"] = df["כיוון רוח (מעלות)"].apply(get_wind_type)

# סינון: השארת שעות האור בלבד (06:00 בבוקר עד 18:00 בערב)
df_daylight = df[pd.to_datetime(df["זמן"], format="%d/%m %H:%M").dt.hour.between(6, 18)]

# חיפוש שעות עם תנאים אידיאליים
best_conditions = df_daylight[
    (df_daylight["גובה גל (מ)"] >= 0.7) & 
    (df_daylight["זמן מחזור (שניות)"] >= 6) & 
    (df_daylight["סוג רוח"] == "אוף-שור 💨")
]

st.subheader("🏄 המלצות לסשן")
if not best_conditions.empty:
    st.success("נמצאו חלונות זמן קלאסיים! אוף-שור מחליק את המים ופותח את הקיר לפמפומים וקארבים. הנה השעות:")
    st.dataframe(best_conditions[["זמן", "גובה גל (מ)", "זמן מחזור (שניות)", "מהירות רוח (קמש)"]], hide_index=True)
elif df_daylight["גובה גל (מ)"].max() < 0.5:
    st.warning("הים צפוי להיות פלטה בימים הקרובים. זמן טוב לאימון סרפסקיט ביבשה לשיפור מיקום הרגליים.")
else:
    st.info("אין תנאי אוף-שור מושלמים בימים הקרובים, אבל שווה לבדוק בטבלה מתי הרוח חלשה.")

# הצגת גרף גבהים
st.subheader("גרף גובה גלים (כל היממה)")
st.line_chart(df.set_index("זמן")["גובה גל (מ)"])

# הצגת הטבלה המלאה לשעות האור
st.subheader("התחזית המלאה (שעות אור)")
st.dataframe(df_daylight[["זמן", "גובה גל (מ)", "זמן מחזור (שניות)", "סוג רוח", "מהירות רוח (קמש)"]], hide_index=True)