import os
from datetime import date

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_replace, lower, round as spark_round


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")


def combine_f1_weather():
    current_day = "20260601"

    races_path = os.path.join(
        DATALAKE_ROOT,
        "formatted",
        "jolpica",
        "races",
        current_day,
        "races.parquet",
    )

    weather_path = os.path.join(
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

    spark = (
        SparkSession.builder
        .appName("CombineF1Weather")
        .master("local[*]")
        .getOrCreate()
    )

    races_df = spark.read.parquet(races_path)
    weather_df = spark.read.parquet(weather_path)

    races_df = races_df.withColumn(
        "race_key",
        regexp_replace(
            regexp_replace(
                regexp_replace(lower(col("race_name")), " ", "_"),
                "/",
                "_",
            ),
            "-",
            "_",
        ),
    )
    
    weather_df = weather_df.drop("race_name")

    final_df = races_df.join(
        weather_df,
        on=["season", "round", "race_key"],
        how="inner",
    )

    final_df = final_df.withColumn(
        "weather_risk_score",
        spark_round(
            (col("total_precipitation") * 2) + col("max_wind_speed"),
            2,
        ),
    )

    final_df = final_df.select(
        col("season"),
        col("round"),
        col("race_name"),
        col("circuit_name"),
        col("date"),
        col("locality"),
        col("country"),
        col("latitude"),
        col("longitude"),
        col("avg_temperature"),
        col("min_temperature"),
        col("max_temperature"),
        col("total_precipitation"),
        col("max_wind_speed"),
        col("weather_risk_score"),
    )

    os.makedirs(output_dir, exist_ok=True)

    pandas_df = final_df.toPandas()

    output_file = os.path.join(
        output_dir,
        "race_weather.parquet"
    )

    pandas_df.to_parquet(
        output_file,
        index=False
    )

    print(f"Fichier usage Spark créé : {output_dir}")
    print(f"Nombre de lignes fusionnées : {final_df.count()}")
    final_df.show(10, truncate=False)

    spark.stop()


if __name__ == "__main__":
    combine_f1_weather()