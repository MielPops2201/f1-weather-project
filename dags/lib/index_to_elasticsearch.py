import os
from datetime import date

import pandas as pd
import requests


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
DATALAKE_ROOT = os.path.join(PROJECT_ROOT, "data")

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_NAME = "f1_weather_race"


def index_to_elasticsearch():
    current_day = date.today().strftime("%Y%m%d")

    input_path = os.path.join(
        DATALAKE_ROOT,
        "usage",
        "f1_weather_analysis",
        "race_weather",
        current_day,
    )

    df = pd.read_parquet(input_path)

    records = df.to_dict(orient="records")

    for record in records:
        doc_id = f"{record['season']}_{record['round']}"

        url = f"{ELASTICSEARCH_URL}/{INDEX_NAME}/_doc/{doc_id}"

        response = requests.put(url, json=record, timeout=30)
        response.raise_for_status()

    print(f"{len(records)} documents indexés dans Elasticsearch : {INDEX_NAME}")


if __name__ == "__main__":
    index_to_elasticsearch()