import json
import os
import time
from datetime import date, datetime

import pandas as pd
import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def clean_race_name(race_name):
    return (
        race_name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace("__", "_")
    )


def fetch_weather_from_races():
    current_day = date.today().strftime("%Y%m%d")
    today = date.today()

    races_file = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "races",
        current_day,
        "races.parquet",
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "open_meteo",
        "weather",
        current_day,
    )

    os.makedirs(output_dir, exist_ok=True)

    races_df = pd.read_parquet(races_file)

    fetched_count = 0
    skipped_future_count = 0
    skipped_existing_count = 0
    error_count = 0

    for _, race in races_df.iterrows():
        season = int(race["season"])
        round_number = int(race["round"])
        race_name = race["race_name"]
        race_date_str = race["date"]
        latitude = float(race["latitude"])
        longitude = float(race["longitude"])

        race_date = datetime.strptime(race_date_str, "%Y-%m-%d").date()

        race_key = clean_race_name(race_name)
        file_name = f"{season}_{round_number}_{race_key}.json"
        output_file = os.path.join(output_dir, file_name)

        # Open-Meteo archive ne peut pas donner la météo historique des courses futures
        if race_date > today:
            print(f"SKIP future race: {season} round {round_number} - {race_name} - {race_date_str}")
            skipped_future_count += 1
            continue

        # Évite de retélécharger si le fichier existe déjà
        if os.path.exists(output_file):
            print(f"SKIP existing file: {file_name}")
            skipped_existing_count += 1
            continue

        url = (
            "https://archive-api.open-meteo.com/v1/archive"
            f"?latitude={latitude}"
            f"&longitude={longitude}"
            f"&start_date={race_date_str}"
            f"&end_date={race_date_str}"
            "&hourly=temperature_2m,precipitation,wind_speed_10m"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            weather_data = response.json()

            if "hourly" not in weather_data:
                print(f"ERROR no hourly data: {season} round {round_number} - {race_name}")
                error_count += 1
                continue

            final_json = {
                "metadata": {
                    "season": season,
                    "round": round_number,
                    "race_name": race_name,
                    "race_key": race_key,
                    "race_date": race_date_str,
                    "circuit_name": race["circuit_name"],
                    "locality": race["locality"],
                    "country": race["country"],
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "weather": weather_data,
            }

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(final_json, file, indent=4)

            print(f"OK météo récupérée: {season} round {round_number} - {race_name}")
            fetched_count += 1

            time.sleep(0.3)

        except Exception as error:
            print(f"ERROR météo: {season} round {round_number} - {race_name} - {error}")
            error_count += 1

    print("\nRésumé météo")
    print(f"Fichiers météo créés : {fetched_count}")
    print(f"Fichiers déjà existants : {skipped_existing_count}")
    print(f"Courses futures ignorées : {skipped_future_count}")
    print(f"Erreurs : {error_count}")


if __name__ == "__main__":
    fetch_weather_from_races()