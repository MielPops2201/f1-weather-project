# F1 Weather Analytics

## Project Overview

This project combines Formula 1 race data and historical weather data to analyze weather conditions during Formula 1 Grand Prix events.

The pipeline automatically:

1. Retrieves Formula 1 race data from Jolpica API.
2. Retrieves historical weather data from Open-Meteo.
3. Stores raw data in a Data Lake.
4. Formats and transforms data into Parquet.
5. Combines F1 and weather datasets.
6. Loads the final dataset into Elasticsearch.
7. Visualizes results through Kibana dashboards.

---

## Architecture

Jolpica API
        \
         -> Raw -> Formatted -> Usage -> Elasticsearch -> Kibana
        /
Open-Meteo API

                ^
                |
             Airflow

---

## Technologies

- Python
- Apache Airflow
- Docker
- PostgreSQL
- Elasticsearch
- Kibana
- Pandas
- Parquet

---

## Data Lake Structure

```text
data/
├── raw/
├── formatted/
└── usage/
```