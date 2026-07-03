import os
import django
import pandas as pd
import ast

from django.db import connection
from django.contrib.auth.models import User
from recommender.models import Course, Category, Interaction, UserProfile

# ==============================
# SETUP DJANGO
# ==============================
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# ==============================
# CLEAN FUNCTION
# ==============================
def clean_list(val):
    if pd.isna(val):
        return []

    if isinstance(val, str):
        val = val.strip()

        if val.startswith("[") and val.endswith("]"):
            try:
                val = ast.literal_eval(val)
            except:
                return []
        else:
            return [v.strip().lower() for v in val.split(",") if v.strip()]

    if isinstance(val, list):
        return [str(v).strip().lower() for v in val if v]

    return []

# ==============================
# RATING FUNCTION
# ==============================
def compute_rating(wp):
    if wp >= 80:
        return 1.0
    elif wp >= 50:
        return 0.7
    elif wp >= 20:
        return 0.4
    else:
        return 0.1

# ==============================
# LOAD DATA (CHEMIN PROPRE)
# ==============================
BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_pipeline", "data")
BASE_DIR = os.path.abspath(BASE_DIR) + "/"

items = pd.read_csv(BASE_DIR + "final_items.csv")
users = pd.read_csv(BASE_DIR + "final_users.csv")
interactions = pd.read_csv(BASE_DIR + "final_interactions.csv")

# ==============================
# RESET DB
# ==============================
print("Reset DB...")

with connection.cursor() as cursor:
    cursor.execute("TRUNCATE TABLE recommender_interaction RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE recommender_userprofile RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE auth_user RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE recommender_course RESTART IDENTITY CASCADE;")
    cursor.execute("TRUNCATE TABLE recommender_category RESTART IDENTITY CASCADE;")

print("DB reset OK")

# ==============================
# CATEGORIES
# ==============================
category_map = {}

for _, row in items.iterrows():
    themes = clean_list(row["Theme"])

    for t in themes:
        if t and t not in category_map:
            category_map[t] = Category.objects.create(name=t)

# ==============================
# COURSES
# ==============================
course_map = {}

for _, row in items.iterrows():

    themes = clean_list(row["Theme"])

    if themes:
        category = category_map.get(themes[0])
    else:
        category, _ = Category.objects.get_or_create(name="non défini")

    course = Course.objects.create(
        title=str(row["name"]),
        description=str(row["description"]),
        difficulty=str(row["Difficulty"]),
        tags=str(row["Software"]),
        category=category
    )

    course_map[row["item_id"]] = course

# ==============================
# USERS
# ==============================
user_map = {}

for _, row in users.iterrows():
    user = User.objects.create_user(
        username=str(row["user_id"]),
        password="1234"
    )

    user_map[row["user_id"]] = user

    UserProfile.objects.update_or_create(
        user=user,
        defaults={
            "interests": row.get("interests", ""),
            "skill_level": row.get("level", "beginner")
        }
    )

# ==============================
# INTERACTIONS
# ==============================
print("Création interactions...")

for _, row in interactions.iterrows():

    user_id = row["user_id"]
    item_id = row["item_id"]

    if user_id in user_map and item_id in course_map:

        wp = float(row["watch_percentage"]) if not pd.isna(row.get("watch_percentage")) else 0

        rating_new = 0.7 * compute_rating(wp) + 0.3 * (wp / 100)

        Interaction.objects.create(
            user=user_map[user_id],
            course=course_map[item_id],
            rating=rating_new,
            watch_percentage=wp,
            viewed=True
        )

print("BASE OK")