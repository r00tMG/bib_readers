import joblib
import pandas as pd

# Charger le modèle sauvegardé
df, tfidf, cosine_sim = joblib.load("./models/modele_recommandation.pkl")

def recommander(livre_id: int, n: int = 4):
    if livre_id not in df["id"].values:
        return pd.DataFrame()

    idx = df.index[df["id"] == livre_id][0]
    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n + 1]
    recos = df.iloc[[i[0] for i in scores]][["id", "titre","stock","rating", "image_url"]]
    return recos.to_dict(orient="records")
