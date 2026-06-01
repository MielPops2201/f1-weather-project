import pandas as pd
import os

# ── Base directory du projet ─────────────────────────────
BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../../")
)

# ── Fichiers d'entrée ────────────────────────────────────
F1_FILE = os.path.join(
    BASE_DIR,
    "data/formatted/f1/results_2024.csv"
)

WEATHER_FILE = os.path.join(
    BASE_DIR,
    "data/formatted/weather/weather_2024.csv"
)

# ── Fichier de sortie ────────────────────────────────────
OUTPUT_FILE = os.path.join(
    BASE_DIR,
    "data/formatted/f1_weather_combined.csv"
)

# ── Charger les datasets ─────────────────────────────────
print("📥 Chargement des données...")

f1_df = pd.read_csv(
    F1_FILE,
    sep=",",
    encoding="utf-8"
)

weather_df = pd.read_csv(
    WEATHER_FILE,
    sep=",",
    encoding="utf-8"
)

print(f"   F1 : {len(f1_df)} lignes")
print(f"   Weather : {len(weather_df)} lignes")

# ── Fusion des données ───────────────────────────────────
print("\n🔗 Fusion des datasets...")

combined_df = f1_df.merge(
    weather_df,
    on=["season", "round"],
    how="left"
)

# ── Sauvegarde ───────────────────────────────────────────
combined_df.to_csv(
    OUTPUT_FILE,
    index=False
)

# ── Résultat ─────────────────────────────────────────────
print("\n✅ Dataset combiné créé")

print(f"\n📁 Emplacement :")
print(OUTPUT_FILE)

print("\n📊 Aperçu :")
print(combined_df.head())