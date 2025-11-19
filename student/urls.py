from django.urls import path
from . import views


# URL patterns for the student app. These minimal routes match the template
# filenames and the `{% url '...' %}` usages in the templates so navigation
# and reverse lookups work while the app is still under development.

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("dashboard/", views.student_dashboard, name="student_dashboard"),
    path("teacher/dashboard/", views.teacher_dashboard, name="teacher_dashboard"),
    path("add/", views.add_student, name="add_student"),
    path("<int:pk>/", views.student_details, name="student_details"),
    path("marks/<int:student_id>/update/", views.update_mark, name="update_mark"),
    path("results/", views.student_results, name="student_results"),
    # path("public-results/", views.public_results, name="public_results"),
    path("edit/<str:slug>/", views.edit_student, name="edit_student"),
    path("delete/<str:slug>/", views.delete_student, name="delete_student"),
    # Teacher CRUD
    path("teachers/", views.teacher_list, name="teacher_list"),
    path("teachers/add/", views.add_teacher, name="add_teacher"),
    path("teachers/<int:pk>/", views.teacher_details, name="teacher_details"),
    path("teachers/edit/<str:slug>/", views.edit_teacher, name="edit_teacher"),
    path("teachers/delete/<str:slug>/", views.delete_teacher, name="delete_teacher"),
    # Teacher Operations
    path("teacher/marks/", views.teacher_marks, name="teacher_marks"),
    path("teacher/departments/", views.department_list, name="department_list"),
    path("teacher/departments/add/", views.add_department, name="add_department"),
    path("teacher/subjects/", views.subject_list, name="subject_list"),
    path("teacher/subjects/add/", views.add_subject, name="add_subject"),
    path(
        "teachers/department/",
        views.teachers_in_department,
        name="teachers_in_department",
    ),
    path(
        "teachers/<slug:slug>/",
        views.teacher_detail,
        name="teacher_details_public",
    ),
    path(
        "teachers/<slug:slug>/assignment/create/",
        views.create_assignment,
        name="create_assignment_for_teacher",
    ),
    path("assignments/create/", views.create_assignment, name="create_assignment"),
    path("my-assignments/", views.my_assignments, name="my_assignments"),
]
