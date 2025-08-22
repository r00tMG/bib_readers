import pandas as pd
import re

df = pd.read_csv("livres_bruts.csv")

# Nettoyer la description
df["description"] = df["description"].apply(lambda x: re.sub(r"\s+", " ", str(x)).strip())

# Remplacer description vide par titre
df["description"] = df.apply(lambda row: row["description"] if row["description"] else row["title"], axis=1)

# Vérifier
print(df.head())

# Sauvegarder
df.to_csv("livres_nettoyes.csv", index=False, encoding="utf-8")
print(" Données nettoyées et sauvegardées dans livres_nettoyes.csv")
