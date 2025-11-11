"""
URL configuration for Home project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView, RedirectView
from django.conf import settings
from django.conf.urls.static import static

from student.views import view_student


try:
    # STATIC_URL is defined in settings; use it to build the redirect target for
    # the favicon. If it's not present for some reason, fall back to '/static/'.
    STATIC_URL = settings.STATIC_URL
except Exception:
    STATIC_URL = "/static/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("schoo.urls")),
    path("student/", include("student.urls")),
    path("students/<slug:slug>/", view_student, name="view_student"),
    # Short-term routes to match the static-like links in the templates
    # (these templates were built as static HTML originally). These
    # TemplateView routes prevent 404s when the UI links to
    # /student-dashboard.html, /student-details.html, /edit-student.html.
    path(
        "student-dashboard.html",
        TemplateView.as_view(template_name="Students/student-dashboard.html"),
    ),
    path(
        "student-details.html",
        TemplateView.as_view(template_name="Students/student-details.html"),
    ),
    path(
        "edit-student.html",
        TemplateView.as_view(template_name="Students/edit-student.html"),
    ),
    # Serve a favicon at /favicon.ico to avoid 404 noise in dev.
    path(
        "favicon.ico", RedirectView.as_view(url=STATIC_URL + "assets/img/favicon.png")
    ),
    path("authentication/", include("home_auth.urls")),
]

# Serve static files during development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    # Serve uploaded media files during development (only when DEBUG=True)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
