import pandas as pd
import json
import os

# ── Racine du projet ─────────────────────────────────────
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

# ── Fichiers ─────────────────────────────────────────────
INPUT_FILE = os.path.join(
    BASE_DIR,
    "data/raw/f1/results_2024.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data/formatted/f1/results_2024.csv"
)

# ── Charger JSON ─────────────────────────────────────────
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = json.load(f)

races = content["data"]

rows = []

# ── Transformation ───────────────────────────────────────
for race in races:

    for result in race["Results"]:

        rows.append({
            "season": race["season"],
            "round": int(race["round"]),
            "race_name": race["raceName"],
            "date": race["date"],

            "circuit_id": race["Circuit"]["circuitId"],
            "circuit_name": race["Circuit"]["circuitName"],

            "driver_id": result["Driver"]["driverId"],

            "driver": (
                result["Driver"]["givenName"]
                + " "
                + result["Driver"]["familyName"]
            ),

            "constructor": result["Constructor"]["name"],

            "grid": int(result["grid"]),
            "position": int(result["position"]),
            "points": float(result["points"]),

            "status": result["status"]
        })

# ── DataFrame ────────────────────────────────────────────
df = pd.DataFrame(rows)

df["date"] = pd.to_datetime(df["date"])

# ── Créer dossier si absent ──────────────────────────────
os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

# ── Sauvegarde CSV ───────────────────────────────────────
df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ── Résultat ─────────────────────────────────────────────
print("\n✅ CSV F1 créé")

print(f"\n📁 Emplacement :")
print(OUTPUT_FILE)

print("\n📊 Aperçu :")
print(df.head())