import os
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")

DATE_VERSION = "20260601"


def combine_driver_weather():

    driver_path = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "driver_results",
        DATE_VERSION,
        "driver_results.parquet",
    )

    weather_path = os.path.join(
        DATALAKE_ROOT,
        "usage",
        "f1_weather_analysis",
        "race_weather",
        DATE_VERSION,
        "race_weather.parquet",
    )

    output_dir = os.path.join(
        DATALAKE_ROOT,
        "usage",
        "f1_weather_analysis",
        "driver_weather_performance",
        DATE_VERSION,
    )

    os.makedirs(output_dir, exist_ok=True)

    drivers_df = pd.read_parquet(driver_path)
    weather_df = pd.read_parquet(weather_path)

    final_df = drivers_df.merge(
        weather_df,
        on=["season", "round", "race_name"],
        how="left",
    )

    output_file = os.path.join(
        output_dir,
        "driver_weather_performance.parquet",
    )

    final_df.to_parquet(output_file, index=False)

    print(f"Fichier créé : {output_file}")
    print(f"Nombre de lignes : {len(final_df)}")
    print(final_df.head())


if __name__ == "__main__":
    combine_driver_weather()