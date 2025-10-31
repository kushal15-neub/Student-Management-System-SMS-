from django.shortcuts import render


# Restored minimal student views so `student.urls` can import them.
def student_list(request):
    """Render the student listing page."""
    return render(request, "Students/students.html")


def add_student(request):
    """Render the add-student form (placeholder)."""
    if request.method == "POST":
        # placeholder: in a real app you'd validate/save a form and redirect
        return render(request, "Students/students.html")
    return render(request, "Students/add-student.html")


def student_details(request, pk=None):
    """Render a student's detail page. (placeholder)"""
    return render(request, "Students/student-details.html")


def edit_student(request, pk=None):
    """Render an edit form for a student (placeholder)."""
    return render(request, "Students/edit-student.html")
