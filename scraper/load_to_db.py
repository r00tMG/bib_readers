import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

# ---- Charger le fichier .env ----
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(" La variable DATABASE_URL n'est pas définie dans le fichier .env")

# ---- Charger le CSV nettoyé ----
df = pd.read_csv("livres_nettoyes.csv")

# ---- Connexion PostgreSQL ----
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print(" Connexion réussie à PostgreSQL via .env")

    # ---- Insertion des données ----
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO livres (title, description, price, availability, rating, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            row["title"],
            row["description"],
            row["price"],
            row["availability"],
            row["rating"],
            row["image_url"]
        ))

    conn.commit()
    print(" Données insérées dans PostgreSQL")

except Exception as e:
    print(" Erreur :", e)

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
