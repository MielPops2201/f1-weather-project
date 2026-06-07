import os

import pandas as pd
import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")

DATE_VERSION = "20260601"
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "f1_driver_weather_performance"


def index_driver_weather_to_elasticsearch():
    input_path = os.path.join(
        DATALAKE_ROOT,
        "usage",
        "f1_weather_analysis",
        "driver_weather_performance",
        DATE_VERSION,
        "driver_weather_performance.parquet",
    )

    df = pd.read_parquet(input_path)
    records = df.to_dict(orient="records")

    for record in records:
        doc_id = f"{record['season']}_{record['round']}_{record['driver_id']}"
        url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_doc/{doc_id}"

        response = requests.put(url, json=record, timeout=30)
        response.raise_for_status()

    print(f"{len(records)} documents indexés dans Elasticsearch : {INDEX_NAME}")


if __name__ == "__main__":
    index_driver_weather_to_elasticsearch()