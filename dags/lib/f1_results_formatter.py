import json
import os

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")

DATE_VERSION = "20260601"


def format_results():
    input_dir = os.path.join(
        DATALAKE_ROOT,
        "raw",
        "jolpica",
        "results",
        DATE_VERSION,
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "driver_results",
        DATE_VERSION,
    )

    os.makedirs(output_dir, exist_ok=True)

    rows = []

    for file_name in os.listdir(input_dir):
        if not file_name.endswith(".json"):
            continue

        input_file = os.path.join(input_dir, file_name)

        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

        races = data["MRData"]["RaceTable"].get("Races", [])

        for race in races:
            season = int(race["season"])
            round_number = int(race["round"])
            race_name = race["raceName"]

            for result in race.get("Results", []):
                driver = result["Driver"]
                constructor = result["Constructor"]

                rows.append(
                    {
                        "season": season,
                        "round": round_number,
                        "race_name": race_name,
                        "driver_id": driver.get("driverId"),
                        "driver_code": driver.get("code"),
                        "driver_name": f"{driver.get('givenName')} {driver.get('familyName')}",
                        "constructor_id": constructor.get("constructorId"),
                        "constructor_name": constructor.get("name"),
                        "grid": int(result.get("grid", 0)),
                        "position_order": int(result.get("positionOrder", 0)),
                        "position_text": result.get("positionText"),
                        "points": float(result.get("points", 0)),
                        "laps": int(result.get("laps", 0)),
                        "status": result.get("status"),
                    }
                )

    df = pd.DataFrame(rows)

    output_file = os.path.join(output_dir, "driver_results.parquet")
    df.to_parquet(output_file, index=False)

    print(f"Fichier résultats pilotes formatted créé : {output_file}")
    print(f"Nombre de lignes résultats pilotes : {len(df)}")
    print(df.head())


if __name__ == "__main__":
    format_results()