import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

# Membaca dataset
day_df = pd.read_csv("dashboard/day_data.csv")
hour_df = pd.read_csv("dashboard/hour_data.csv")

def create_daily_sharing_df(df):
    daily_sharing_df = df.resample(rule="D", on="date").agg({
        "casual": "sum",
        "registered": "sum",
        "total": "sum"
    })
    daily_sharing_df = daily_sharing_df.reset_index()
    daily_sharing_df.rename(columns={
        "casual": "casual_count",
        "registered": "registered_count",
        "total": "total_sharing"
    }, inplace=True)
    return daily_sharing_df

def create_bygender_df(df):
    bygender_df = df.groupby(by="gender").customer_id.nunique().reset_index()
    bygender_df.rename(columns={
        "customer_id": "customer_count"
    }, inplace=True)
    
    return bygender_df

def create_season_df(df):
    season_df = df.groupby(by="season").total.nunique().reset_index()
    season_df.rename(columns={
        "total": "season_count"
    }, inplace=True)
    return season_df

def create_weekday_df(df):
    weekday_df = df.groupby(by="weekday").total.nunique().reset_index()
    weekday_df.rename(columns={
        "total": "weekday_count"
    }, inplace=True)
    return weekday_df

def create_weather_df(df):
    weather_df = df.groupby(by="weather").total.nunique().reset_index()
    weather_df.rename(columns={
        "total": "weather_count"
    }, inplace=True)
    return weather_df

def create_year_df(df):
    year_df = df.groupby("year").total.sum().sort_values(ascending=False).reset_index()
    return year_df

def create_rfm_df(df):
    last_date = df["date"].max()
    rfm_df = df.groupby("registered").agg(
    Recency=('date', lambda x: (last_date - x.max()).days),
    Frequency=('date', 'count'),
    Monetary=('total', 'sum')  
    ).reset_index()

    return rfm_df

# Konversi tipe data date
day_df["date"] = pd.to_datetime(day_df["date"])
hour_df["date"] = pd.to_datetime(hour_df["date"])

# Membuat Komponen Filter
min_date = day_df["date"].min()
max_date = day_df["date"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("Logo.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Menyimpan nilai filter ke main_df
main_df = day_df[(day_df["date"] >= str(start_date)) & 
                (day_df["date"] <= str(end_date))]

daily_sharing_df = create_daily_sharing_df(main_df)
season_df = create_season_df(main_df)
weekday_df = create_weekday_df(main_df)
weather_df = create_weather_df(main_df)
year_df = create_year_df(main_df)
rfm_df = create_rfm_df(main_df)

# Main Content
st.header("Dashboard Penyewaan Sepeda")
st.subheader("Total Bike Sharing")
    
col1, col2, col3 = st.columns([2,1,1])
    
with col1:
    total_sharing = daily_sharing_df.total_sharing.sum()
    st.metric("Total Sharing", value=total_sharing)

with col2:
    total_casual = daily_sharing_df.casual_count.sum() 
    st.metric("Total Casual", value=total_casual)

with col3:
    total_registered = daily_sharing_df.registered_count.sum()
    st.metric("Total Registered", value=total_registered)

# Performa Penyewaan
st.subheader("Performa Bike Sharing")

# Berdasarkan Musim
st.markdown("<h5>Berdasarkan Musim</h5>", unsafe_allow_html=True)
color = {
    "Fall": "#8B4513",
    "Spring": "#E3D8C8",
    "Summer": "#E3D8C8", 
    "Winter": "#E3D8C8"
}
season_df["category"] = season_df["season"]

# Membuat grafik batang untuk season
plt.figure(figsize=(10, 5))
sns.barplot(
    x = "season",
    y = "season_count",
    data = season_df.sort_values(by="season", ascending=False),
    palette = color,
    hue = "category",
    legend = False,
    errorbar = None
)
plt.title("Total Counts by Season", fontsize=15)
st.pyplot(plt)

# Membuat grafik batang untuk hari
st.markdown("<h5>Berdasarkan Hari</h5>", unsafe_allow_html=True)
color={
    "Fri": "#8B4513",
    "Sun": "#E3D8C8",
    "Mon": "#E3D8C8",
    "Tue": "#E3D8C8",
    "Wed": "#E3D8C8",
    "Thu": "#E3D8C8",
    "Sat": "#E3D8C8"
}
weekday_df["category"] = weekday_df["weekday"]

plt.figure(figsize=(10, 5))
sns.barplot(
    x = "weekday",
    y = "weekday_count",
    data = weekday_df.sort_values(by="weekday", ascending=False),
    order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
    palette = color,
    hue = "category",
    legend = False,
    errorbar = None
)
plt.title("Total Counts by Weekday", fontsize=15)
st.pyplot(plt)

# Membuat grafik batang untuk cuaca
st.markdown("<h5>Berdasarkan Cuaca</h5>", unsafe_allow_html=True)
color={
    "Clear": "#8B4513",
    "Mist & Cloudy": "#E3D8C8",
    "Light rain": "#E3D8C8",
}
weather_df["category"] = weather_df["weather"]

plt.figure(figsize=(10, 5))
sns.barplot(
    x = "weather",
    y = "weather_count",
    data = weather_df.sort_values(by="weather", ascending=False),
    palette = color,
    hue = "category",
    legend = False,
    errorbar = None
)
plt.title("Total Counts by Weather", fontsize=15)
st.pyplot(plt)

# Grafik bulanan
st.subheader("Grafik Sharing Beberapa Bulan Terakhir")
plt.figure(figsize=(20, 7))

sns.lineplot(
    x = "date",
    y = "total_sharing",
    data = daily_sharing_df.sort_values(by="date").reset_index(),
    marker = "o",
    color = "#6BAED6",
    errorbar = None
)
    
st.pyplot(plt)

st.caption('Copyright (c) Syahbagus Radithya Haryo Santoso 2024')