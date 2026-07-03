import os
import pandas as pd
from functools import lru_cache

from django.conf import settings
from .models import Interaction

# ==========================================
# LOAD MODEL (1 seule fois)
# ==========================================
import joblib

import joblib

BASE_DIR = os.path.join(
    settings.BASE_DIR,
    "recommender",
    "ml_models"
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "svd_model.pkl"
)

model = joblib.load(MODEL_PATH)


# ==========================================
# LOAD INTERACTIONS FROM DB
# ==========================================
def get_interactions_df():

    qs = Interaction.objects.select_related("user", "course").all()

    data = []

    for i in qs:
        data.append({
            "user_id": i.user.id,   # ✅ FIX ICI
            "item_id": i.course.id,
            "watch_percentage": i.watch_percentage,
            "rating": i.rating
        })

    return pd.DataFrame(data)


# ==========================================
# CACHE ( amélioration performance)
# ==========================================

def get_interactions_df_cached():
    return get_interactions_df()

# ==========================================
# HYBRID RECOMMENDER
# ==========================================
def recommend(user_id, n=10):

    df = get_interactions_df_cached()

    if df.empty:
        return []

    user_id = int(user_id) if isinstance(user_id, str) and user_id.isdigit() else user_id
    all_items = df["item_id"].unique()

    user_data = df[df["user_id"] == user_id]

    # 🔥 items déjà vus
    seen_items = set(user_data["item_id"])

    candidates = list(set(all_items) - seen_items)

    # 🔥 popularité
    item_pop = df["item_id"].value_counts(normalize=True)

    # 🔥 comportement utilisateur
    user_mean = user_data["watch_percentage"].mean() / 100 if len(user_data) > 0 else 0.5

    scores = []

    for item in candidates:

        try:
            svd_score = model.predict(user_id, item).est
        except:
            svd_score = 0

        pop_score = item_pop.get(item, 0)

        # 🔥 AJOUT PERSONNALISATION
        final_score = (
            0.5 * svd_score +
            0.3 * pop_score +
            0.2 * user_mean
        )

        scores.append((item, final_score))

    scores.sort(key=lambda x: x[1], reverse=True)

    return [int(item) for item, _ in scores[:n]]

def track_interaction(user, course, watch_increment=10, rating=None):

    obj, created = Interaction.objects.get_or_create(
        user=user,
        course=course
    )

    #  mise à jour watch
    obj.watch_percentage = min(100, obj.watch_percentage + watch_increment)

    #  mise à jour rating
    if rating is not None:
        obj.rating = rating

    obj.save()