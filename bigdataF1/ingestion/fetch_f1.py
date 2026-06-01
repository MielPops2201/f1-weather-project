"""
Ingestion F1 - Jolpica API
Récupère : saisons, circuits, résultats de courses, classement pilotes
Stocke en JSON dans data/raw/f1/
"""

import requests
import json
import os
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL = "http://api.jolpi.ca/ergast/f1"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "f1")
CURRENT_SEASON = 2024  # Change à 2025 quand la saison est terminée

# ── Helpers ────────────────────────────────────────────────────────────────────

def save_json(data: dict, filename: str) -> None:
    """Sauvegarde un dict en JSON dans le dossier raw/f1/"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Sauvegardé : {filepath}")


def fetch(url: str, params: dict = None) -> dict:
    """Appel HTTP GET avec gestion des erreurs basique"""
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Erreur lors de la requête {url} : {e}")
        return {}


def fetch_all_pages(url: str, result_key: str, limit: int = 100) -> list:
    """
    Parcourt toutes les pages d'une réponse paginée Jolpica.
    result_key : chemin dans MRData vers la liste de résultats
    Exemple : fetch_all_pages(url, "RaceTable.Races")
    """
    offset = 0
    all_items = []

    while True:
        data = fetch(url, params={"limit": limit, "offset": offset})
        if not data:
            break

        mr_data = data.get("MRData", {})
        total = int(mr_data.get("total", 0))

        # Navigue dans les clés imbriquées (ex: "RaceTable.Races")
        items = mr_data
        for key in result_key.split("."):
            items = items.get(key, {})

        if isinstance(items, list):
            all_items.extend(items)
        else:
            break

        offset += limit
        if offset >= total:
            break

    return all_items


# ── Fonctions d'ingestion ──────────────────────────────────────────────────────

def ingest_circuits() -> None:
    """Récupère tous les circuits F1"""
    print("\n📡 Ingestion des circuits...")
    url = f"{BASE_URL}/circuits.json"
    circuits = fetch_all_pages(url, "CircuitTable.Circuits")

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": url,
        "count": len(circuits),
        "data": circuits,
    }
    save_json(result, "circuits.json")
    print(f"     → {len(circuits)} circuits récupérés")


def ingest_races(season: int) -> None:
    """Récupère le calendrier des courses d'une saison"""
    print(f"\n📡 Ingestion du calendrier {season}...")
    url = f"{BASE_URL}/{season}.json"
    races = fetch_all_pages(url, "RaceTable.Races")

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": url,
        "season": season,
        "count": len(races),
        "data": races,
    }
    save_json(result, f"races_{season}.json")
    print(f"     → {len(races)} courses récupérées")


def ingest_results(season: int) -> None:
    """Récupère les résultats de toutes les courses d'une saison"""
    print(f"\n📡 Ingestion des résultats {season}...")
    url = f"{BASE_URL}/{season}/results.json"
    races_with_results = fetch_all_pages(url, "RaceTable.Races")

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": url,
        "season": season,
        "count": len(races_with_results),
        "data": races_with_results,
    }
    save_json(result, f"results_{season}.json")
    print(f"     → Résultats de {len(races_with_results)} courses récupérés")


def ingest_driver_standings(season: int) -> None:
    """Récupère le classement général des pilotes d'une saison"""
    print(f"\n📡 Ingestion du classement pilotes {season}...")
    url = f"{BASE_URL}/{season}/driverstandings.json"
    data = fetch(url)

    standings_list = (
        data.get("MRData", {})
            .get("StandingsTable", {})
            .get("StandingsLists", [])
    )

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": url,
        "season": season,
        "data": standings_list,
    }
    save_json(result, f"driver_standings_{season}.json")
    print(f"     → Classement pilotes récupéré")


def ingest_qualifying(season: int) -> None:
    """Récupère les résultats de qualifications d'une saison"""
    print(f"\n📡 Ingestion des qualifications {season}...")
    url = f"{BASE_URL}/{season}/qualifying.json"
    qualifying = fetch_all_pages(url, "RaceTable.Races")

    result = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "source": url,
        "season": season,
        "count": len(qualifying),
        "data": qualifying,
    }
    save_json(result, f"qualifying_{season}.json")
    print(f"     → Qualifications de {len(qualifying)} courses récupérées")


# ── Point d'entrée ─────────────────────────────────────────────────────────────

def run():
    print("=" * 55)
    print("🏎️  INGESTION F1 - Jolpica API")
    print(f"    Saison cible : {CURRENT_SEASON}")
    print(f"    Dossier de sortie : {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 55)

    ingest_circuits()
    ingest_races(CURRENT_SEASON)
    ingest_results(CURRENT_SEASON)
    ingest_driver_standings(CURRENT_SEASON)
    ingest_qualifying(CURRENT_SEASON)

    print("\n✅ Ingestion F1 terminée !")


if __name__ == "__main__":
    run()