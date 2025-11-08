from django.urls import path
from . import views


# URL patterns for the student app. These minimal routes match the template
# filenames and the `{% url '...' %}` usages in the templates so navigation
# and reverse lookups work while the app is still under development.
urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("add/", views.add_student, name="add_student"),
    path("<int:pk>/", views.student_details, name="student_details"),
    path("<int:pk>/edit/", views.edit_student, name="edit_student"),
    path("marks/<int:student_id>/update/", views.update_mark, name="update_mark"),
    path("results/", views.student_results, name="student_results"),
    path("public-results/", views.public_results, name="public_results"),
]
