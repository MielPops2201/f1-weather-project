from datetime import datetime, timedelta
from lib.index_to_elasticsearch import index_to_elasticsearch

from airflow import DAG
from airflow.operators.python import PythonOperator

from lib.f1_fetcher import fetch_races
from lib.f1_formatter import format_races
from lib.weather_from_races import fetch_weather_from_races
from lib.weather_formatter import format_weather
from lib.combine_f1_weather import combine_f1_weather
from lib.f1_results_fetcher import fetch_results_from_races
from lib.f1_results_formatter import format_results
from lib.combine_driver_weather import combine_driver_weather
from lib.index_driver_weather_to_elasticsearch import index_driver_weather_to_elasticsearch


default_args = {
    "owner": "f1-weather-team",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


with DAG(
    dag_id="f1_weather_pipeline",
    description="Pipeline F1 + météo : ingestion, formatting et combinaison",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["f1", "weather", "big-data"],
) as dag:

    fetch_races_task = PythonOperator(
        task_id="fetch_races",
        python_callable=fetch_races,
    )

    format_races_task = PythonOperator(
        task_id="format_races",
        python_callable=format_races,
    )

    fetch_weather_task = PythonOperator(
        task_id="fetch_weather_from_races",
        python_callable=fetch_weather_from_races,
    )

    format_weather_task = PythonOperator(
        task_id="format_weather",
        python_callable=format_weather,
    )

    combine_task = PythonOperator(
        task_id="combine_f1_weather",
        python_callable=combine_f1_weather,
    )

    index_task = PythonOperator(
        task_id="index_to_elasticsearch",
        python_callable=index_to_elasticsearch,
    )

    fetch_results_task = PythonOperator(
        task_id="fetch_results_from_races",
        python_callable=fetch_results_from_races,
    )

    format_results_task = PythonOperator(
        task_id="format_results",
        python_callable=format_results,
    )

    combine_driver_weather_task = PythonOperator(
        task_id="combine_driver_weather",
        python_callable=combine_driver_weather,
    )

    index_driver_weather_task = PythonOperator(
        task_id="index_driver_weather_to_elasticsearch",
        python_callable=index_driver_weather_to_elasticsearch,
    )

    fetch_races_task >> format_races_task

    format_races_task >> fetch_weather_task >> format_weather_task >> combine_task >> index_task

    format_races_task >> fetch_results_task >> format_results_task

    [combine_task, format_results_task] >> combine_driver_weather_task >> index_driver_weather_task