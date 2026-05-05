import json
import os
from datetime import date

import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def fetch_current_f1_results():
    current_day = date.today().strftime("%Y%m%d")

    target_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "jolpica",
        "race_results",
        current_day,
    )

    os.makedirs(target_dir, exist_ok=True)

    url = "https://api.jolpi.ca/ergast/f1/current/results.json"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    output_file = os.path.join(target_dir, "race_results.json")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Fichier créé : {output_file}")

def fetch_races():
    current_day = date.today().strftime("%Y%m%d")

    target_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "jolpica",
        "races",
        current_day,
    )

    os.makedirs(target_dir, exist_ok=True)

    url = "https://api.jolpi.ca/ergast/f1/current.json"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    output_file = os.path.join(target_dir, "races.json")

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    print(f"Fichier races créé : {output_file}")

if __name__ == "__main__":
    fetch_current_f1_results()

if __name__ == "__main__":
    fetch_races()