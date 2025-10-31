from django.urls import path
from . import views


# URL patterns for the student app. These minimal routes match the template
# filenames and the `{% url '...' %}` usages in the templates so navigation
# and reverse lookups work while the app is still under development.
urlpatterns = [

    path("", views.student_list, name="student_list"),
    path("add/", views.add_student, name="add_student"),
    path("<int:pk>/", views.student_details, name="student_details"),
    path("<int:pk>/edit/", views.edit_student, name="edit_student"),
]
