# recommender/train_svd.py

from pathlib import Path

import joblib
import pandas as pd

from surprise import Dataset
from surprise import Reader
from surprise import SVD

from recommender.models import Interaction


def retrain_model():

    print("Chargement des interactions...")

    qs = Interaction.objects.all()

    data = []

    for i in qs:

        score = (
            0.7 * float(i.rating)
            +
            0.3 * float(i.watch_percentage / 10)
        )

        score = min(10, max(0, score))

        data.append([
            int(i.user_id),
            int(i.course_id),
            float(score)
        ])

    if len(data) == 0:
        print("Aucune interaction trouvée")
        return

    df = pd.DataFrame(
        data,
        columns=[
            "user",
            "item",
            "rating"
        ]
    )

    print("Nombre interactions :", len(df))
    print("Nombre utilisateurs :", df["user"].nunique())
    print("Nombre cours :", df["item"].nunique())

    print(df["rating"].describe())

    reader = Reader(
        rating_scale=(0, 10)
    )

    dataset = Dataset.load_from_df(
        df[["user", "item", "rating"]],
        reader
    )

    trainset = dataset.build_full_trainset()

    print("Entraînement SVD...")

    model = SVD(
        n_factors=100,
        n_epochs=50,
        lr_all=0.005,
        reg_all=0.02,
        random_state=42
    )

    model.fit(trainset)

    MODEL_PATH = (
        Path(__file__).resolve().parent
        / "ml_models"
        / "svd_model.pkl"
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_PATH
    )

    print("Modèle sauvegardé :", MODEL_PATH)
    print("Recommandation mise à jour avec succès")