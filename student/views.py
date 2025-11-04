from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import Student, Mark
from .forms import MarkForm


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


def _is_teacher(user):
    if not user.is_authenticated:
        return False
    return user.is_staff or user.groups.filter(name__iexact="Teachers").exists()


@login_required
@user_passes_test(_is_teacher)
def update_mark(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    initial_subject = request.GET.get("subject", "")
    initial_exam = request.GET.get("exam", "")

    existing = None
    if initial_subject and initial_exam:
        existing = Mark.objects.filter(
            student=student, subject=initial_subject, exam_name=initial_exam
        ).first()

    if request.method == "POST":
        # For updates, try to locate the target record based on hidden fields
        subject = request.POST.get("subject")
        exam_name = request.POST.get("exam_name")
        instance = Mark.objects.filter(
            student=student, subject=subject, exam_name=exam_name
        ).first()
        form = MarkForm(request.POST, instance=instance)
        if form.is_valid():
            mark = form.save(commit=False)
            mark.student = student
            mark.updated_by = request.user
            mark.save()
            messages.success(request, "Marks updated successfully.")
            return redirect("student_details", pk=student.pk)
        messages.error(request, "Please correct the errors below.")
    else:
        form = MarkForm(instance=existing)
        if initial_subject:
            form.fields["subject"].initial = initial_subject
        if initial_exam:
            form.fields["exam_name"].initial = initial_exam

    context = {
        "student": student,
        "form": form,
    }
    return render(request, "Students/update-mark.html", context)
