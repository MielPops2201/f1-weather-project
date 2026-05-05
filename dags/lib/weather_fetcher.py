import json
import os
from datetime import date

import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def fetch_weather():
    current_day = date.today().strftime("%Y%m%d")

    target_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "weather",
        "monaco",
        current_day,
    )

    os.makedirs(target_dir, exist_ok=True)

    # Monaco coordinates
    latitude = 43.7384
    longitude = 7.4246

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    output_file = os.path.join(target_dir, "weather.json")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Fichier météo créé : {output_file}")


if __name__ == "__main__":
    fetch_weather()