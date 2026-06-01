import json
import os
from datetime import date

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def format_races():
    current_day = date.today().strftime("%Y%m%d")

    input_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "jolpica",
        "races",
        current_day,
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "races",
        current_day,
    )

    os.makedirs(output_dir, exist_ok=True)

    rows = []

    for file_name in os.listdir(input_dir):
        if not file_name.startswith("races_") or not file_name.endswith(".json"):
            continue

        input_file = os.path.join(input_dir, file_name)

        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        races = data["MRData"]["RaceTable"]["Races"]

        for race in races:
            location = race["Circuit"]["Location"]

            rows.append(
                {
                    "season": int(race["season"]),
                    "round": int(race["round"]),
                    "race_name": race["raceName"],
                    "circuit_name": race["Circuit"]["circuitName"],
                    "date": race["date"],
                    "locality": location["locality"],
                    "country": location["country"],
                    "latitude": float(location["lat"]),
                    "longitude": float(location["long"]),
                }
            )

    df = pd.DataFrame(rows)

    output_file = os.path.join(output_dir, "races.parquet")
    df.to_parquet(output_file, index=False)

    print(f"Fichier races formatted créé : {output_file}")
    print(f"Nombre de courses : {len(df)}")
    print(df.head())


if __name__ == "__main__":
    format_races()