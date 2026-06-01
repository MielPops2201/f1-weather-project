import json
import os
import time
from datetime import date

import pandas as pd
import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def fetch_weather_from_races():
    current_day = date.today().strftime("%Y%m%d")

    races_file = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "races",
        current_day,
        "races.parquet",
    )

    races_df = pd.read_parquet(races_file)

    for _, race in races_df.iterrows():
        race_name = race["race_name"]
        race_date = race["date"]
        latitude = race["latitude"]
        longitude = race["longitude"]

        clean_race_name = (
            race_name.lower()
            .replace(" ", "_")
            .replace("/", "_")
            .replace("-", "_")
        )

        target_dir = os.path.join(
            DATALAKE_ROOT,
            "raw",
            "open_meteo",
            clean_race_name,
            current_day,
        )

        os.makedirs(target_dir, exist_ok=True)

        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&start_date={race_date}"
            f"&end_date={race_date}"
            "&hourly=temperature_2m,precipitation,wind_speed_10m"
        )

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        weather_data = response.json()

        output_file = os.path.join(target_dir, "weather.json")

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(weather_data, file, indent=4)

        print(f"Météo récupérée : {race_name} - {race_date}")

        time.sleep(0.5)


if __name__ == "__main__":
    fetch_weather_from_races()