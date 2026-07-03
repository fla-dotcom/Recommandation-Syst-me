from django.http import JsonResponse
from .services import recommend, track_interaction
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Interaction
from django.core.paginator import Paginator
from .models import Course, Category
from django.core.mail import send_mail
from django.db.models import Q
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd


# API JSON
def recommend_api(request, user_id):
    try:
        recs = recommend(user_id)

        return JsonResponse({
            "user_id": user_id,
            "recommendations": recs
        })

    except Exception as e:
        return JsonResponse({"error": str(e)})


# PAGE HTML
def recommendations_page(request):

    if not request.user.is_authenticated:
        return redirect("login")

    user_id = request.user.id
    ids = recommend(user_id)

    from django.db.models import Case, When

    courses = []
    if ids:
        preserved_order = Case(*[
            When(id=pk, then=pos) for pos, pk in enumerate(ids)
        ])

        courses = Course.objects.filter(id__in=ids).order_by(preserved_order)

    # AJOUT CRITIQUE
    popular = Course.objects.all()[:8]
    recent = Course.objects.order_by("-id")[:8]

    return render(request, "recommendations.html", {
        "items": courses,
        "ids": ids,
        "popular": popular,
        "recent": recent
    })

def course_detail(request, course_id):

    course = Course.objects.get(id=course_id)

    if request.user.is_authenticated:
        track_interaction(
            user=request.user,
            course=course,
            watch_increment=10
        )

    # =========================
    # COURS SIMILAIRES
    # =========================

    all_courses = Course.objects.all()

    df = pd.DataFrame(list(
        all_courses.values(
            "id",
            "title",
            "description",
            "tags"
        )
    ))

    df["content"] = (
        df["title"].fillna("") + " " +
        df["description"].fillna("") + " " +
        df["tags"].fillna("")
    )

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(df["content"])

    cosine_sim = cosine_similarity(tfidf_matrix)

    idx = df[df["id"] == course.id].index[0]

    similarity_scores = list(enumerate(cosine_sim[idx]))

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Exclure le cours lui-même
    similarity_scores = similarity_scores[1:5]

    similar_ids = [
        int(df.iloc[i[0]]["id"])
        for i in similarity_scores
    ]

    related_courses = Course.objects.filter(
        id__in=similar_ids
    )

    return render(
        request,
        "course_detail.html",
        {
            "course": course,
            "related_courses": related_courses
        }
    )

def course_list(request):

    query = request.GET.get("q", "")

    courses = Course.objects.all()

    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )

    context = {
        "courses": courses,
        "query": query
    }

    return render(
        request,
        "courses.html",
        context
    )

def home(request):

    recommended_courses = []

    if request.user.is_authenticated:
        ids = recommend(request.user.id)

        if ids:
            from django.db.models import Case, When

            preserved_order = Case(*[
                When(id=pk, then=pos) for pos, pk in enumerate(ids)
            ])

            recommended_courses = Course.objects.filter(
                id__in=ids
            ).order_by(preserved_order)

    #  IMPORTANT
    popular = Course.objects.all()[:8]
    recent = Course.objects.order_by("-id")[:8]

    return render(request, "home.html", {
        "recommended": recommended_courses,
        "popular": popular,
        "recent": recent
    })

# =========================
# LOGIN
# =========================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        remember_me = request.POST.get("remember_me")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # REMEMBER ME
            if not remember_me:
                request.session.set_expiry(0)  # expire à la fermeture navigateur
            else:
                request.session.set_expiry(1209600)  # 2 semaines

            return redirect("home")
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect")

    return render(request, "login.html")


# =========================
# REGISTER
# =========================
def register_view(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email=request.POST.get("email")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Les mots de passe ne correspondent pas")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Utilisateur déjà existant")
            return redirect("register")


        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=username
        )

        login(request, user)
        return redirect("home")

    return render(request, "login.html")  # même page avec tabs


# =========================
# LOGOUT
# =========================
def logout_view(request):
    logout(request)
    return redirect("login")

# =========================
# about
# =========================
def about(request):
    return render(request, "about.html")
# =========================
# courses
# =========================


def courses(request):

    courses = Course.objects.all()

    # ================= SEARCH =================
    search = (
            request.GET.get("q", "")
            or request.GET.get("search", "")
    ).strip()

    if search:
        courses = courses.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )

    # ================= CATEGORY =================

    category = (request.GET.get("category")or "").strip()

    if category:
        courses = courses.filter(
            category_id=category
        )

    # ================= DIFFICULTY =================

    difficulty = (request.GET.get("difficulty")or "").strip().lower()

    if difficulty:
        courses = courses.filter(
            difficulty__iexact=difficulty
        )

    # ================= SORT =================

    sort = (request.GET.get("sort")or "").strip()

    if sort == "old":
        courses = courses.order_by("id")
    else:
        courses = courses.order_by("-id")

    # Nombre de résultats après filtrage
    result_count = courses.count()

    # ================= PAGINATION =================

    paginator = Paginator(courses, 12)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    # ================= CONTEXT =================

    categories = Category.objects.all()

    return render(request, "courses.html", {
        "courses": page_obj,
        "categories": categories,
        "total_courses": paginator.count,
        "search": search,
        "result_count": result_count
    })




def track_interaction(user, course, watch_increment=0, rating=None):

    obj, created = Interaction.objects.get_or_create(
        user=user,
        course=course
    )

    obj.watch_percentage = min(100, obj.watch_percentage + watch_increment)

    if rating:
        obj.rating = rating

    obj.save()


# =========================
# contact
# =========================

from django.conf import settings

def contact(request):

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        subject = request.POST.get("subject")
        message = request.POST.get("message")

        full_message = f"""
Nom : {name}

Email : {email}

Message :
{message}
"""

        send_mail(
            subject,
            full_message,
            settings.EMAIL_HOST_USER,
            ['fadmalarhzaoui1@gmail.com'],
            fail_silently=False,
        )

        messages.success(
            request,
            "Votre message a été envoyé avec succès."
        )

        return redirect('contact')

    return render(request, 'contact.html')