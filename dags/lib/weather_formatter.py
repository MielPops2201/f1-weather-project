import json
import os
from datetime import date

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def format_weather():
    current_day = date.today().strftime("%Y%m%d")

    raw_weather_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "open_meteo",
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "open_meteo",
        "weather",
        current_day,
    )

    os.makedirs(output_dir, exist_ok=True)

    rows = []

    for race_folder in os.listdir(raw_weather_dir):
        race_path = os.path.join(raw_weather_dir, race_folder, current_day)
        weather_file = os.path.join(race_path, "weather.json")

        if not os.path.exists(weather_file):
            continue

        with open(weather_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        hourly = data["hourly"]

        temperature = hourly["temperature_2m"]
        precipitation = hourly["precipitation"]
        wind_speed = hourly["wind_speed_10m"]
        times = hourly["time"]

        rows.append(
            {
                "race_key": race_folder,
                "weather_date": times[0].split("T")[0],
                "avg_temperature": sum(temperature) / len(temperature),
                "min_temperature": min(temperature),
                "max_temperature": max(temperature),
                "total_precipitation": sum(precipitation),
                "max_wind_speed": max(wind_speed),
            }
        )

    df = pd.DataFrame(rows)

    output_file = os.path.join(output_dir, "weather.parquet")
    df.to_parquet(output_file, index=False)

    print(f"Fichier météo formatted créé : {output_file}")
    print(df.head())


if __name__ == "__main__":
    format_weather()