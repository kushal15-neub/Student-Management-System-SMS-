from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include
from .views import *

# URL patterns for the student app. These minimal routes match the template
# filenames and the `{% url '...' %}` usages in the templates so navigation
# and reverse lookups work while the app is still under development.


urlpatterns = [
    path("signup/", signup_view, name="signup"),
    path("login/", login_view, name="login"),
    path("forgot-password/", forgot_password_view, name="forgot-password"),
    path("reset-password/<str:token>/", reset_password_view, name="reset-password"),
    path("logout/", logout_view, name="logout"),
    path("profile/", profile_view, name="profile"),
]
