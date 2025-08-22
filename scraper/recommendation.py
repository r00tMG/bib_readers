import os
import psycopg2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from dotenv import load_dotenv

# ---- Charger les variables d'environnement ----
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(" La variable DATABASE_URL n'est pas définie dans le fichier .env")

# ---- Charger les données depuis PostgreSQL ----
try:
    conn = psycopg2.connect(DATABASE_URL)
    df = pd.read_sql("SELECT id, title, description FROM livres", conn)
    conn.close()
    print(" Données chargées depuis PostgreSQL")
except Exception as e:
    print(" Erreur de connexion ou lecture :", e)
    raise

# ---- Prétraitement et vectorisation TF-IDF ----
tfidf = TfidfVectorizer(stop_words="english")
tfidf_matrix = tfidf.fit_transform(df["description"].fillna(""))

# ---- Calcul de la similarité cosinus ----
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# ---- Sauvegarde du modèle ----
joblib.dump((df, tfidf, cosine_sim), "modele_recommandation.pkl")
print(" Modèle de recommandation sauvegardé")

# ---- Fonction de recommandation ----
def recommander(livre_id, n=5):
    if livre_id not in df["id"].values:
        print(f" Livre avec id={livre_id} non trouvé")
        return pd.DataFrame()
    
    idx = df.index[df["id"] == livre_id][0]
    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]  # ignorer le livre lui-même
    recos = df.iloc[[i[0] for i in scores]][["id","title"]]
    return recos

# ---- Exemple ----
if __name__ == "__main__":
    print(recommander(livre_id=1))
