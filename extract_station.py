from zoneinfo import ZoneInfo

import os
import duckdb
import requests 
from datetime import datetime, timezone
import json 
from dotenv import load_dotenv
load_dotenv()

con = duckdb.connect(
    "md:dockcast_fr",
    config={
        "motherduck_token": os.environ["MOTHERDUCK_TOKEN"],
        "storage_compatibility_version": "v1.5.6"
    }
)

url = "https://gbfs.lyft.com/gbfs/2.3/bkn/en/station_status.json"
response = requests.get(url)
response.raise_for_status()
data = response.json()

stations = data['data']['stations']

print("worked")

con.execute("""
    CREATE SCHEMA IF NOT EXISTS bronze;

    CREATE TABLE IF NOT EXISTS bronze.raw_trips(
        station_id VARCHAR, 
        num_bikes_available INTEGER,
        num_ebikes_available INTEGER,
        num_docks_available INTEGER,
        is_installed BOOLEAN,
        is_renting BOOLEAN,
        is_returning BOOLEAN,
        last_reported TIMESTAMP
    );
""")

timestamp = current_time = datetime.now(ZoneInfo("America/New_York"))

for station in stations:
    con.execute("""
        INSERT INTO bronze.raw_trips
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        station["station_id"],
        station["num_bikes_available"],
        station["num_ebikes_available"],
        station["num_docks_available"],
        station["is_installed"],
        station["is_renting"],
        station["is_returning"],
        timestamp
    ])

print( stations[0]["num_bikes_available"] )
print("worked")
con.close()