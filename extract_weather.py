import duckdb
import requests 
from datetime import datetime, timezone
import json 
from zoneinfo import ZoneInfo
con = duckdb.connect("dockcast.duckdb")

locations = [
    {"longitude": -74.05169461801283, "latitude": 40.75327580084569},
    {"longitude": -73.88443854495146, "latitude": 40.76229696731788},
    {"longitude": -73.935633004101, "latitude": 40.819575336786635},
    {"longitude": -73.96957433071144, "latitude": 40.692040244144934},
    {"longitude": -73.88629762675619, "latitude": 40.884666520492786},
    {"longitude": -73.93790968942305, "latitude": 40.812662814724014},
]


con.execute("""
    CREATE SCHEMA IF NOT EXISTS bronze;

    CREATE TABLE IF NOT EXISTS bronze.raw_weather(
        timestamp TIMESTAMP,
        longitude FLOAT,
        latitude FLOAT,
        temperature FLOAT,
        humidity FLOAT,
        precipitation_probability FLOAT,
        cloudcover FLOAT,
        windspeed FLOAT
    );
""")

current_time = datetime.now(ZoneInfo("America/New_York")).strftime("%H:%M")
hours = int(current_time.split(":")[0])
minutes = int(current_time.split(":")[1])
num_days = 2 if hours >= 23 else 1




for location in locations:
    url = f"https://api.open-meteo.com/v1/forecast?latitude={location['latitude']}&longitude={location['longitude']}&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,cloudcover,windspeed_10m&forecast_days={num_days}&timezone=America%2FNew_York"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    time = hours+1

    con.execute("""
        INSERT INTO bronze.raw_weather
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        datetime.now(ZoneInfo("America/New_York")),
        location["longitude"],
        location["latitude"],
        data["hourly"]["temperature_2m"][time],
        data["hourly"]["relativehumidity_2m"][time],
        data["hourly"]["precipitation_probability"][time],
        data["hourly"]["cloudcover"][time],
        data["hourly"]["windspeed_10m"][time]
    ])

con.close()