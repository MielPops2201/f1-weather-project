"""
Ingestion Météo - Open-Meteo API (gratuite, sans clé)
Pour chaque circuit F1, récupère la météo historique du jour de la course.
Stocke en JSON dans data/raw/weather/
"""

import requests
import json
import os
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────────
WEATHER_URL = "https://archive-api.open-meteo.com/v1/archive"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "weather")

# Variables météo à récupérer (historique)
WEATHER_VARIABLES = [
    "temperature_2m_max",       # Température max du jour (°C)
    "temperature_2m_min",       # Température min du jour (°C)
    "precipitation_sum",        # Pluie totale (mm)
    "windspeed_10m_max",        # Vitesse max du vent (km/h)
    "winddirection_10m_dominant", # Direction dominante du vent (degrés)
    "weathercode",              # Code météo WMO (0=clair, 61=pluie, etc.)
]

# Dictionnaire des circuits F1 avec leurs coordonnées GPS
# Source : positions officielles des circuits
CIRCUITS_COORDS = {
    "bahrain":         {"lat": 26.0325,  "lon": 50.5106,  "name": "Bahrain International Circuit"},
    "jeddah":          {"lat": 21.6322,  "lon": 39.1044,  "name": "Jeddah Corniche Circuit"},
    "albert_park":     {"lat": -37.8497, "lon": 144.9680, "name": "Albert Park Circuit"},
    "suzuka":          {"lat": 34.8431,  "lon": 136.5407, "name": "Suzuka Circuit"},
    "shanghai":        {"lat": 31.3389,  "lon": 121.2198, "name": "Shanghai International Circuit"},
    "miami":           {"lat": 25.9581,  "lon": -80.2389, "name": "Miami International Autodrome"},
    "imola":           {"lat": 44.3439,  "lon": 11.7167,  "name": "Autodromo Enzo e Dino Ferrari"},
    "monaco":          {"lat": 43.7347,  "lon": 7.4208,   "name": "Circuit de Monaco"},
    "villeneuve":      {"lat": 45.5000,  "lon": -73.5228, "name": "Circuit Gilles Villeneuve"},
    "catalunya":       {"lat": 41.5700,  "lon": 2.2611,   "name": "Circuit de Barcelona-Catalunya"},
    "red_bull_ring":   {"lat": 47.2197,  "lon": 14.7647,  "name": "Red Bull Ring"},
    "silverstone":     {"lat": 52.0786,  "lon": -1.0169,  "name": "Silverstone Circuit"},
    "hungaroring":     {"lat": 47.5789,  "lon": 19.2486,  "name": "Hungaroring"},
    "spa":             {"lat": 50.4372,  "lon": 5.9714,   "name": "Circuit de Spa-Francorchamps"},
    "zandvoort":       {"lat": 52.3888,  "lon": 4.5408,   "name": "Circuit Zandvoort"},
    "monza":           {"lat": 45.6156,  "lon": 9.2811,   "name": "Autodromo Nazionale Monza"},
    "baku":            {"lat": 40.3725,  "lon": 49.8533,  "name": "Baku City Circuit"},
    "marina_bay":      {"lat": 1.2914,   "lon": 103.8639, "name": "Marina Bay Street Circuit"},
    "americas":        {"lat": 30.1328,  "lon": -97.6411, "name": "Circuit of The Americas"},
    "rodriguez":       {"lat": 19.4042,  "lon": -99.0907, "name": "Autodromo Hermanos Rodriguez"},
    "interlagos":      {"lat": -23.7036, "lon": -46.6997, "name": "Autodromo Jose Carlos Pace"},
    "las_vegas":       {"lat": 36.1147,  "lon": -115.1728, "name": "Las Vegas Strip Circuit"},
    "losail":          {"lat": 25.4900,  "lon": 51.4542,  "name": "Losail International Circuit"},
    "yas_marina":      {"lat": 24.4672,  "lon": 54.6031,  "name": "Yas Marina Circuit"},
}


# ── Helpers ────────────────────────────────────────────────────────────────────

def save_json(data: dict, filename: str) -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Sauvegardé : {filepath}")


def fetch_weather_for_race(circuit_id: str, race_date: str, lat: float, lon: float) -> dict:
    """
    Récupère la météo historique pour un circuit à une date donnée.
    race_date : format "YYYY-MM-DD"
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": race_date,
        "end_date": race_date,
        "daily": ",".join(WEATHER_VARIABLES),
        "timezone": "UTC",
    }

    try:
        response = requests.get(WEATHER_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        # Extraire les valeurs du jour (index 0 car on demande 1 seul jour)
        daily = data.get("daily", {})
        weather_day = {
            "circuit_id": circuit_id,
            "race_date": race_date,
            "latitude": lat,
            "longitude": lon,
        }
        for var in WEATHER_VARIABLES:
            values = daily.get(var, [None])
            weather_day[var] = values[0] if values else None

        return weather_day

    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur météo pour {circuit_id} ({race_date}): {e}")
        return {}


def load_races_file(season: int) -> list:
    """
    Charge le fichier races_{season}.json produit par fetch_f1.py
    pour récupérer les dates et circuits des courses.
    """
    races_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "raw", "f1", f"races_{season}.json"
    )
    if not os.path.exists(races_path):
        print(f"  ⚠️  Fichier introuvable : {races_path}")
        print("     Lance d'abord fetch_f1.py pour générer les données F1.")
        return []

    with open(races_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    return content.get("data", [])


# ── Fonctions d'ingestion ──────────────────────────────────────────────────────

def ingest_weather_for_season(season: int) -> None:
    """
    Pour chaque course de la saison, récupère la météo historique du jour.
    Nécessite que fetch_f1.py ait déjà été lancé.
    """
    print(f"\n📡 Ingestion météo pour la saison {season}...")
    races = load_races_file(season)

    if not races:
        return

    weather_records = []

    for race in races:
        circuit_id = race.get("Circuit", {}).get("circuitId", "unknown")
        race_date = race.get("date")  # format "YYYY-MM-DD"
        race_name = race.get("raceName", "Unknown Race")
        round_num = race.get("round", "?")

        # Récupère les coordonnées depuis notre dictionnaire
        coords = CIRCUITS_COORDS.get(circuit_id)
        if not coords:
            print(f"  ⚠️  Coordonnées inconnues pour : {circuit_id} — ignoré")
            continue

        print(f"  🌤️  Round {round_num} - {race_name} ({race_date})...")
        weather = fetch_weather_for_race(
            circuit_id=circuit_id,
            race_date=race_date,
            lat=coords["lat"],
            lon=coords["lon"],
        )

        if weather:
            # Enrichir avec les infos de la course
            weather["race_name"] = race_name
            weather["round"] = round_num
            weather["season"] = season
            weather["circuit_name"] = coords["name"]
            weather_records.append(weather)

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": WEATHER_URL,
        "season": season,
        "count": len(weather_records),
        "data": weather_records,
    }
    save_json(result, f"weather_{season}.json")
    print(f"\n     → Météo récupérée pour {len(weather_records)} courses")


def ingest_weather_single_race(circuit_id: str, race_date: str) -> None:
    """
    Utilitaire : récupère la météo pour un seul circuit/date.
    Utile pour tester ou mettre à jour une seule course.
    """
    print(f"\n📡 Ingestion météo pour {circuit_id} le {race_date}...")
    coords = CIRCUITS_COORDS.get(circuit_id)
    if not coords:
        print(f"  ❌ Circuit inconnu : {circuit_id}")
        return

    weather = fetch_weather_for_race(
        circuit_id=circuit_id,
        race_date=race_date,
        lat=coords["lat"],
        lon=coords["lon"],
    )

    if weather:
        filename = f"weather_{circuit_id}_{race_date}.json"
        save_json(weather, filename)


# ── Point d'entrée ─────────────────────────────────────────────────────────────

def run(season: int = 2024):
    print("=" * 55)
    print("🌦️  INGESTION MÉTÉO - Open-Meteo (archive)")
    print(f"    Saison cible : {season}")
    print(f"    Dossier de sortie : {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 55)

    ingest_weather_for_season(season)

    print("\n✅ Ingestion météo terminée !")


if __name__ == "__main__":
    run(season=2024)