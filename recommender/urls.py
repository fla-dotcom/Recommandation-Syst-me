from django.urls import path
from .views import recommend_api, recommendations_page
from . import views
from .views import login_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("recommend/<int:user_id>/", recommend_api),
    path("page/<int:user_id>/", recommendations_page),
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("recommendations/", recommendations_page, name="recommendations"),
    path("home/", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("courses/", views.courses, name="courses"),
    path("courses/", views.course_list, name="courses"),
    path("contact/", views.contact, name="contact"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    #login:
    path("login/", login_view, name="login"),

    #  PASSWORD RESET FLOW
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name="password_reset.html"
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name="password_reset_done.html"
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name="password_reset_confirm.html"
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name="password_reset_complete.html"
         ),
         name='password_reset_complete'),

]

