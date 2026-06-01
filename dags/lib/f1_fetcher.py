import json
import os
import time
from datetime import date

import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def fetch_races(start_year=2018, end_year=2026):
    current_day = date.today().strftime("%Y%m%d")

    target_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "jolpica",
        "races",
        current_day,
    )

    os.makedirs(target_dir, exist_ok=True)

    for season in range(start_year, end_year + 1):
        url = f"https://api.jolpi.ca/ergast/f1/{season}.json"

        print(f"Récupération des courses F1 {season}...")

        response = requests.get(url, timeout=30)
        response.raise_for_status()

        data = response.json()

        output_file = os.path.join(target_dir, f"races_{season}.json")

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        print(f"Fichier créé : {output_file}")

        time.sleep(0.5)


if __name__ == "__main__":
    fetch_races()