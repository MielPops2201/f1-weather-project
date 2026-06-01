import json
import os
from datetime import date

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def safe_avg(values):
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return None
    return sum(clean_values) / len(clean_values)


def safe_sum(values):
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return None
    return sum(clean_values)


def safe_min(values):
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return None
    return min(clean_values)


def safe_max(values):
    clean_values = [v for v in values if v is not None]
    if not clean_values:
        return None
    return max(clean_values)


def format_weather():
    current_day = date.today().strftime("%Y%m%d")

    input_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "open_meteo",
        "weather",
        current_day,
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

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".json"):
            continue

        input_file = os.path.join(input_dir, file_name)

        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        metadata = data["metadata"]
        hourly = data["weather"]["hourly"]

        temperature = hourly["temperature_2m"]
        precipitation = hourly["precipitation"]
        wind_speed = hourly["wind_speed_10m"]

        rows.append(
            {
                "season": metadata["season"],
                "round": metadata["round"],
                "race_key": metadata["race_key"],
                "race_name": metadata["race_name"],
                "weather_date": metadata["race_date"],
                "avg_temperature": safe_avg(temperature),
                "min_temperature": safe_min(temperature),
                "max_temperature": safe_max(temperature),
                "total_precipitation": safe_sum(precipitation),
                "max_wind_speed": safe_max(wind_speed),
            }
        )

    df = pd.DataFrame(rows)

    output_file = os.path.join(output_dir, "weather.parquet")
    df.to_parquet(output_file, index=False)

    print(f"Fichier météo formatted créé : {output_file}")
    print(f"Nombre de lignes météo : {len(df)}")
    print(df.head())


if __name__ == "__main__":
    format_weather()