import json
import os
import time
from datetime import date

import pandas as pd
import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def fetch_results_from_races():
    current_day = "20260601"

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
        "jolpica",
        "results",
        current_day,
    )

    os.makedirs(output_dir, exist_ok=True)

    races_df = pd.read_parquet(races_file)

    created = 0
    skipped = 0
    errors = 0

    for _, race in races_df.iterrows():
        season = int(race["season"])
        round_number = int(race["round"])

        output_file = os.path.join(
            output_dir,
            f"results_{season}_{round_number}.json"
        )

        if os.path.exists(output_file):
            skipped += 1
            print(f"SKIP existing file: results_{season}_{round_number}.json")
            continue

        url = f"https://api.jolpi.ca/ergast/f1/{season}/{round_number}/results.json"

        try:
            print(f"Récupération résultats {season} round {round_number}...")

            response = requests.get(url, timeout=60)
            response.raise_for_status()

            data = response.json()

            with open(output_file, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)

            created += 1
            time.sleep(3)

        except Exception as error:
            errors += 1
            print(f"ERROR {season} round {round_number}: {error}")
            time.sleep(10)

    print("\nRésumé résultats F1")
    print(f"Fichiers créés : {created}")
    print(f"Fichiers déjà existants : {skipped}")
    print(f"Erreurs : {errors}")


if __name__ == "__main__":
    fetch_results_from_races()