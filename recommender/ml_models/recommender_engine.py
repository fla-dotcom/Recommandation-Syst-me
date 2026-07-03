import joblib
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
# Charger modèles
model = joblib.load(BASE_DIR / "svd_model.pkl")
vectorizer = joblib.load(BASE_DIR / "tfidf_vectorizer.pkl")
cosine_sim = joblib.load(BASE_DIR / "cosine_sim.pkl")
item_id_to_index = joblib.load(BASE_DIR / "item_index.pkl")

items = pd.read_csv(BASE_DIR / "items_FINAL.csv")

# content score
def content_score(item_id_1, item_id_2):
    if item_id_1 not in item_id_to_index or item_id_2 not in item_id_to_index:
        return 0

    idx1 = item_id_to_index[item_id_1]
    idx2 = item_id_to_index[item_id_2]

    return cosine_sim[idx1, idx2]


# HYBRID
def hybrid_score(user_id, item_id, alpha=0.9):

    svd_pred = model.predict(user_id, item_id).est

    # ici simplifié (pas de train dataframe)
    return svd_pred


# API simple
def recommend_for_user(user_id, n=10):

    all_items = items["item_id"].values

    scores = [
        (item, hybrid_score(user_id, item))
        for item in all_items
    ]

    scores = sorted(scores, key=lambda x: x[1], reverse=True)

    return [int(item) if item is not None else None for item, score in scores[:n]]