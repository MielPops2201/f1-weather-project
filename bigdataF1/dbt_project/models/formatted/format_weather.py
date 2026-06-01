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
    "data/raw/weather/weather_2024.json"
)

OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data/formatted/weather/weather_2024.csv"
)

# ── Charger JSON ─────────────────────────────────────────
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    content = json.load(f)

weather_data = content["data"]

# ── DataFrame ────────────────────────────────────────────
df = pd.DataFrame(weather_data)

# ── Créer dossier si absent ──────────────────────────────
os.makedirs(
    os.path.dirname(OUTPUT_FILE),
    exist_ok=True
)

# ── Sauvegarde CSV UTF-8 ─────────────────────────────────
df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8"
)

# ── Résultat ─────────────────────────────────────────────
print("\n✅ CSV Weather créé")

print(f"\n📁 Emplacement :")
print(OUTPUT_FILE)

print("\n📊 Aperçu :")
print(df.head())