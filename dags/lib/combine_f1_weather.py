import os
from datetime import date

import pandas as pd


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def clean_race_name(race_name):
    return (
        race_name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("-", "_")
    )


def combine_f1_weather():
    current_day = date.today().strftime("%Y%m%d")

    races_file = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "races",
        current_day,
        "races.parquet",
    )

    weather_file = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "open_meteo",
        "weather",
        current_day,
        "weather.parquet",
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "usage",
        "f1_weather_analysis",
        "race_weather",
        current_day,
    )

    os.makedirs(output_dir, exist_ok=True)

    races_df = pd.read_parquet(races_file)
    weather_df = pd.read_parquet(weather_file)

    races_df["race_key"] = races_df["race_name"].apply(clean_race_name)

    final_df = races_df.merge(
        weather_df,
        on=["season", "round", "race_key"],
        how="inner",
    )

    final_df = final_df[
        [
            "season",
            "round",
            "race_name_x",
            "circuit_name",
            "date",
            "locality",
            "country",
            "latitude",
            "longitude",
            "avg_temperature",
            "min_temperature",
            "max_temperature",
            "total_precipitation",
            "max_wind_speed",
        ]
    ]

    final_df = final_df.rename(
        columns={
            "race_name_x": "race_name"
        }
    )

    output_file = os.path.join(output_dir, "race_weather.parquet")
    final_df.to_parquet(output_file, index=False)

    print(f"Fichier usage créé : {output_file}")
    print(f"Nombre de lignes fusionnées : {len(final_df)}")
    print(final_df.head())


if __name__ == "__main__":
    combine_f1_weather()