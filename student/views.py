from urllib import request
import json
from collections import OrderedDict

from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db import models as django_models
from django.db.models import Q
from django.utils import timezone

from .models import Parent, Student, Mark, Teacher, Department, Subject, Course
from .forms import MarkForm, TeacherForm, TeacherMarkForm
from .models import Teacher, Student, Assignment
from .forms import AssignmentForm, AssignmentAssignForm


# Permission helper functions (must be defined before use in decorators)
def _is_teacher(user):
    """Check if user is a teacher (not admin/staff)"""
    if not user.is_authenticated:
        return False
    return getattr(user, "is_teacher", False) and not user.is_superuser


def _is_admin(user):
    """Check if user is admin/superuser"""
    if not user.is_authenticated:
        return False
    return user.is_superuser or getattr(user, "is_admin", False)


# Restored minimal student views so `student.urls` can import them.
@login_required
@user_passes_test(_is_admin)
def add_student(request):
    """Render the add-student form (placeholder)."""
    if request.method == "POST":
        # placeholder: in a real app you'd validate/save a form and redirect
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        student_id = request.POST.get("student_id")
        gender = request.POST.get("gender")
        date_of_birth = request.POST.get("date_of_birth")
        student_class = request.POST.get("student_class")
        religion = request.POST.get("religion")
        joining_date = request.POST.get("joining_date")
        mobile_number = request.POST.get("mobile_number")
        admission_number = request.POST.get("admission_number")
        section = request.POST.get("section")
        student_image = request.FILES.get("student_image")

        # retrieve parent info
        father_name = request.POST.get("father_name")
        father_occupation = request.POST.get("father_occupation")
        father_mobile = request.POST.get("father_mobile")
        fathers_email = request.POST.get("fathers_email")

        mother_name = request.POST.get("mother_name")
        mother_occupation = request.POST.get("mother_occupation")
        mother_mobile = request.POST.get("mother_mobile")
        mothers_email = request.POST.get("mothers_email")
        permanent_address = request.POST.get("permanent_address")
        present_address = request.POST.get("present_address")

        # save parent
        parent = Parent.objects.create(
            father_name=father_name,
            father_occupation=father_occupation,
            father_mobile=father_mobile,
            father_email=fathers_email,
            mother_name=mother_name,
            mother_occupation=mother_occupation,
            mother_mobile=mother_mobile,
            mother_email=mothers_email,
            present_address=present_address,
        )

        # save student
        department_id = request.POST.get("department")
        department = None
        if department_id:
            department = Department.objects.filter(pk=department_id).first()

        student = Student.objects.create(
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,
            gender=gender,
            date_of_birth=date_of_birth,
            student_class=student_class,
            religion=religion,
            joining_date=joining_date,
            mobile_number=mobile_number,
            admission_number=admission_number,
            section=section,
            student_image=student_image,
            parent=parent,
            department=department,
        )
        messages.success(request, "Student added successfully.")
        # After creating a student redirect to the student list so the user
        # sees the newly added record. The template for the list is
        # `Students/students.html` and the named URL is `student_list`.
        return redirect("student_list")

    # Render the add form on GET (or if POST processing failed).
    departments = Department.objects.all().order_by("name")
    return render(request, "Students/add-student.html", {"departments": departments})


def student_details(request, pk):
    """Render a student's detail page with data from database."""
    student = get_object_or_404(Student.objects.select_related("parent"), pk=pk)
    # Get all marks for this student
    marks = student.marks.all().order_by("exam_name", "subject")
    context = {"student": student, "marks": marks}
    return render(request, "Students/student-details.html", context)


def student_list(request):
    """Render the student listing page with data from database."""
    students = Student.objects.select_related("parent", "department").all()

    # If the current user is a teacher (and not admin), show only students
    # from the teacher's department.
    user = request.user
    if (
        getattr(user, "is_authenticated", False)
        and getattr(user, "is_teacher", False)
        and not _is_admin(user)
    ):
        my_teacher = getattr(user, "teacher_profile", None)
        if my_teacher and my_teacher.department:
            students = students.filter(department=my_teacher.department)
        else:
            students = Student.objects.none()

    context = {"student_list": students}
    return render(request, "Students/students.html", context)


@login_required
@user_passes_test(_is_admin)
def edit_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    parent = student.parent if hasattr(student, "parent") else None

    if request.method == "POST":
        # Student fields - get values and strip whitespace
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        student_id = request.POST.get("student_id", "").strip()
        gender = request.POST.get("gender", "").strip()
        date_of_birth = request.POST.get("date_of_birth", "").strip() or None
        student_class = request.POST.get("student_class", "").strip()
        religion = request.POST.get("religion", "").strip()
        joining_date = request.POST.get("joining_date", "").strip() or None
        mobile_number = request.POST.get("mobile_number", "").strip()
        admission_number = request.POST.get("admission_number", "").strip()
        section = request.POST.get("section", "").strip()
        student_image = request.FILES.get("student_image")

        # Debug: Print received values (remove after testing)
        print(f"DEBUG - Received POST data:")
        print(f"  first_name: '{first_name}'")
        print(f"  last_name: '{last_name}'")
        print(f"  Current student: {student.first_name} {student.last_name}")

        # Parent fields (use multiple possible form field names for safety)
        father_name = request.POST.get("father_name")
        father_occupation = request.POST.get("father_occupation")
        father_mobile = request.POST.get("father_mobile")
        father_email = request.POST.get("father_email") or request.POST.get(
            "fathers_email"
        )

        mother_name = request.POST.get("mother_name")
        mother_occupation = request.POST.get("mother_occupation")
        mother_mobile = request.POST.get("mother_mobile")
        mother_email = request.POST.get("mother_email") or request.POST.get(
            "mothers_email"
        )

        present_address = request.POST.get("present_address")

        # Update or create parent
        if parent:
            parent.father_name = father_name or parent.father_name
            parent.father_occupation = father_occupation or parent.father_occupation
            parent.father_mobile = father_mobile or parent.father_mobile
            parent.father_email = father_email or parent.father_email

            parent.mother_name = mother_name or parent.mother_name
            parent.mother_occupation = mother_occupation or parent.mother_occupation
            parent.mother_mobile = mother_mobile or parent.mother_mobile
            parent.mother_email = mother_email or parent.mother_email

            if present_address:
                parent.present_address = present_address
            parent.save()
        else:
            parent = Parent.objects.create(
                father_name=father_name or "",
                father_occupation=father_occupation or "",
                father_mobile=father_mobile or "",
                father_email=father_email or "",
                mother_name=mother_name or "",
                mother_occupation=mother_occupation or "",
                mother_mobile=mother_mobile or "",
                mother_email=mother_email or "",
                present_address=present_address or "",
            )

        # Update student fields - always update from form values
        # Store old name for comparison
        old_name = f"{student.first_name} {student.last_name}"

        student.first_name = first_name
        student.last_name = last_name
        student.student_id = student_id
        if gender:
            student.gender = gender
        if date_of_birth:
            student.date_of_birth = date_of_birth
        student.student_class = student_class
        student.religion = religion
        if joining_date:
            student.joining_date = joining_date
        student.mobile_number = mobile_number
        student.admission_number = admission_number
        student.section = section
        if student_image:
            student.student_image = student_image
        # department (admin-only edit)
        department_id = request.POST.get("department")
        if department_id:
            department_obj = Department.objects.filter(pk=department_id).first()
            student.department = department_obj
        student.parent = parent

        # Force save and refresh from database
        student.save()
        student.refresh_from_db()

        new_name = f"{student.first_name} {student.last_name}"
        messages.success(
            request,
            f"Student updated successfully. Old: {old_name} → New: {new_name}",
        )
        return redirect("student_list")

    # GET -> render form
    departments = Department.objects.all().order_by("name")
    context = {"student": student, "parent": parent, "departments": departments}
    return render(request, "Students/edit-student.html", context)


@login_required
@user_passes_test(_is_admin)
def delete_student(request, slug):
    if request.method == "POST":
        student = get_object_or_404(Student, slug=slug)
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()
        messages.success(request, f"Student '{student_name}' deleted successfully.")
        return redirect("student_list")
    return HttpResponseForbidden()


@login_required
def student_dashboard(request):
    """Render the student dashboard page with real student insights."""
    # Try to find the Student linked to the current user
    student = getattr(request.user, "student_profile", None)
    if student is None:
        # No direct link found — try a fallback by admission_number == username
        student = Student.objects.filter(admission_number=request.user.username).first()

    context = {
        "student": student,
        "student_cards": {},
        "lessons_today": [],
        "learning_history": [],
        "calendar_events": [],
        "learning_activity_labels": json.dumps([]),
        "learning_activity_scores": json.dumps([]),
        "performance_trends": [],
    }

    if student:
        marks_qs = student.marks.all().order_by("-updated_at")
        marks_list = list(marks_qs)
        assignments_qs = (
            getattr(student, "assignments", Assignment.objects.none())
            .all()
            .order_by("due_date")
        )
        subjects_qs = (
            Subject.objects.filter(department=student.department, is_approved=True)
            if getattr(student, "department", None)
            else Subject.objects.none()
        )

        tests_attended = len(marks_list)
        tests_passed = sum(
            1
            for mark in marks_list
            if mark.max_score and mark.score >= 0.5 * mark.max_score
        )

        context["student_cards"] = {
            "subjects": subjects_qs.count(),
            "assignments": assignments_qs.count(),
            "tests_attended": tests_attended,
            "tests_passed": tests_passed,
        }

        # Build per-subject progress to populate "Today's Lesson" widgets
        subject_progress = {}
        for mark in reversed(marks_list):
            if not mark.max_score:
                continue
            key = mark.subject
            subject_progress.setdefault(key, {"scores": [], "count": 0, "labels": []})
            subject_progress[key]["scores"].append(mark.score / mark.max_score * 100)
            subject_progress[key]["count"] += 1
            subject_progress[key]["labels"].append(
                mark.exam_name
                or (mark.updated_at.strftime("%b %d") if mark.updated_at else "Exam")
            )

        lessons_today = []
        for subject, stats in sorted(
            subject_progress.items(),
            key=lambda item: sum(item[1]["scores"]) / len(item[1]["scores"]),
            reverse=True,
        )[:2]:
            average = round(sum(stats["scores"]) / len(stats["scores"]), 1)
            lessons_today.append(
                {
                    "title": subject,
                    "progress": average,
                    "lessons": stats["count"],
                    "minutes": stats["count"] * 45,
                    "assignments": stats["count"],
                }
            )
        context["lessons_today"] = lessons_today

        # Performance trends data per subject
        performance_trends = []
        for subject, stats in subject_progress.items():
            scores = [round(score, 2) for score in stats["scores"]]
            performance_trends.append(
                {
                    "subject": subject,
                    "labels": stats["labels"],
                    "scores": scores,
                    "latest_score": scores[-1] if scores else 0,
                }
            )
        context["performance_trends"] = performance_trends

        # Learning history combines latest assignments and marks
        history_entries = []
        today = timezone.now().date()
        for assignment in assignments_qs[:5]:
            status = (
                "Completed"
                if assignment.due_date and assignment.due_date < today
                else "In Progress"
            )
            history_entries.append(
                {
                    "label": (
                        assignment.due_date.strftime("%b %d, %I%p")
                        if assignment.due_date
                        else "No due date"
                    ),
                    "title": assignment.title,
                    "status": status,
                }
            )
        for mark in marks_list[:5]:
            history_entries.append(
                {
                    "label": (
                        mark.updated_at.strftime("%b %d, %I:%M %p")
                        if mark.updated_at
                        else "N/A"
                    ),
                    "title": f"{mark.subject} ({mark.exam_name})",
                    "status": f"{mark.score}/{mark.max_score}",
                }
            )
        context["learning_history"] = history_entries[:5]

        # Calendar events sourced from upcoming assignments
        palette = ["blue", "violet", "red", "orange", "green", "indigo"]
        calendar_events = []
        for idx, assignment in enumerate(assignments_qs[:4]):
            calendar_events.append(
                {
                    "title": assignment.title,
                    "time_range": (
                        assignment.due_date.strftime("%b %d")
                        if assignment.due_date
                        else "TBD"
                    ),
                    "color": palette[idx % len(palette)],
                }
            )
        context["calendar_events"] = calendar_events

        # Learning activity chart: monthly average mark percentages
        month_buckets = OrderedDict()
        for mark in marks_list:
            if not mark.updated_at or not mark.max_score:
                continue
            label = mark.updated_at.strftime("%b")
            key = (mark.updated_at.year, mark.updated_at.month, label)
            month_buckets.setdefault(key, []).append(mark.score / mark.max_score * 100)

        if month_buckets:
            sorted_items = sorted(
                month_buckets.items(), key=lambda item: (item[0][0], item[0][1])
            )
            last_items = sorted_items[-6:]
            labels = [item[0][2] for item in last_items]
            scores = [round(sum(values) / len(values), 2) for _, values in last_items]
        else:
            labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            scores = [0, 0, 0, 0, 0, 0]

        context["learning_activity_labels"] = json.dumps(labels)
        context["learning_activity_scores"] = json.dumps(scores)

    return render(request, "Students/student-dashboard.html", context)


@login_required
def teacher_dashboard(request):
    """Teacher/staff dashboard. Uses the same layout as student but allows extra actions."""
    user = request.user
    if not getattr(user, "is_teacher", False):
        messages.error(request, "You do not have access to the teacher dashboard.")
        return redirect("student_dashboard")

    context = {
        "display_name": getattr(user, "first_name", "")
        or user.get_full_name()
        or user.username,
    }
    return render(request, "Teachers/teacher-dashboard.html", context)


# @csrf_exempt
# def public_results(request):
#     """Public (unauthenticated) entry to view results by admission number.

#     WARNING: This endpoint is intentionally permissive to allow previewing
#     results before authentication is implemented. It should be considered
#     temporary — prefer a token-based or authenticated flow in production.
#     The view accepts POST with `admission_number` and optional
#     `date_of_birth` (YYYY-MM-DD) to reduce accidental exposure.
#     """
#     student = None
#     exams = {}

#     if request.method == "POST":
#         admission = request.POST.get("admission_number", "").strip()
#         dob = request.POST.get("date_of_birth", "").strip()

#         if not admission:
#             messages.error(request, "Please provide an admission number.")
#             return render(
#                 request,
#                 "Students/public_results_form.html",
#                 {"student": None, "exams": {}},
#             )

#         qs = Student.objects.filter(admission_number=admission)

#         if dob:
#             try:
#                 from datetime import datetime

#                 # HTML5 date input sends YYYY-MM-DD format, which is what we need
#                 dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
#                 qs = qs.filter(date_of_birth=dob_parsed)
#             except ValueError:
#                 messages.error(
#                     request, "Invalid date format. Please use YYYY-MM-DD format."
#                 )
#                 return render(
#                     request,
#                     "Students/public_results_form.html",
#                     {"student": None, "exams": {}},
#                 )
#             except Exception as e:
#                 messages.error(request, f"Error processing date: {str(e)}")
#                 return render(
#                     request,
#                     "Students/public_results_form.html",
#                     {"student": None, "exams": {}},
#                 )

#         student = qs.first()
#         if not student:
#             messages.error(
#                 request,
#                 f"No student found with admission number: {admission}. Please check and try again.",
#             )
#             return render(
#                 request,
#                 "Students/public_results_form.html",
#                 {"student": None, "exams": {}},
#             )

#         # Build exams grouping and annotate marks (same format as student_results)
#         marks = student.marks.all().order_by("exam_name", "subject")

#         if not marks.exists():
#             messages.warning(
#                 request,
#                 f"Student found, but no marks/results are available yet for {student.first_name} {student.last_name}.",
#             )
#             context = {"student": student, "exams": {}}
#             return render(request, "Students/results.html", context)

#         for m in marks:
#             ex = m.exam_name
#             exams.setdefault(ex, {"marks": [], "total_score": 0, "max_total": 0})
#             exams[ex]["marks"].append(m)
#             exams[ex]["total_score"] += m.score
#             exams[ex]["max_total"] += m.max_score

#         # Compute percent per exam and grade
#         for ex, info in exams.items():
#             if info["max_total"]:
#                 info["percent"] = round(
#                     info["total_score"] * 100.0 / info["max_total"], 2
#                 )
#                 p = info["percent"]
#                 if p >= 90:
#                     info["grade"] = "A+"
#                 elif p >= 80:
#                     info["grade"] = "A"
#                 elif p >= 70:
#                     info["grade"] = "B"
#                 elif p >= 60:
#                     info["grade"] = "C"
#                 elif p >= 50:
#                     info["grade"] = "D"
#                 else:
#                     info["grade"] = "F"
#             else:
#                 info["percent"] = None
#                 info["grade"] = "N/A"

#             # Calculate subject-wise percentages and grades
#             for m in info["marks"]:
#                 if m.max_score:
#                     subj_pct = round(m.score * 100.0 / m.max_score, 2)
#                 else:
#                     subj_pct = None
#                 setattr(m, "subject_percent", subj_pct)
#                 if subj_pct is None:
#                     setattr(m, "subject_grade", None)
#                 elif subj_pct >= 90:
#                     setattr(m, "subject_grade", "A+")
#                 elif subj_pct >= 80:
#                     setattr(m, "subject_grade", "A")
#                 elif subj_pct >= 70:
#                     setattr(m, "subject_grade", "B")
#                 elif subj_pct >= 60:
#                     setattr(m, "subject_grade", "C")
#                 elif subj_pct >= 50:
#                     setattr(m, "subject_grade", "D")
#                 else:
#                     setattr(m, "subject_grade", "F")

#         context = {"student": student, "exams": exams}
#         return render(request, "Students/results.html", context)

#     # GET -> show the public form
#     return render(
#         request, "Students/public_results_form.html", {"student": None, "exams": {}}
#     )


def view_student(request, slug):
    student = get_object_or_404(Student, slug=slug)
    context = {"student": student}
    return render(request, "Students/student-details.html", context)


@login_required
def student_results(request):
    """Allow a logged-in student to view their marks.

    If the logged-in User is linked to a Student via `Student.user`, the view
    will gather marks grouped by `exam_name` and compute totals and percentage
    for each exam. If no linked Student is found, show a helpful message.
    """
    # Try to find the Student linked to the current user
    student = getattr(request.user, "student_profile", None)
    if student is None:
        # No direct link found — try a fallback by admission_number == username
        student = Student.objects.filter(admission_number=request.user.username).first()

    if not student:
        messages.error(request, "No student profile linked to your account.")
        return redirect("student_dashboard")

    # Gather marks and group by exam
    marks = student.marks.all().order_by("exam_name", "subject")
    exams = {}
    for m in marks:
        ex = m.exam_name
        exams.setdefault(ex, {"marks": [], "total_score": 0, "max_total": 0})
        exams[ex]["marks"].append(m)
        exams[ex]["total_score"] += m.score
        exams[ex]["max_total"] += m.max_score

    # Compute percent per exam and grade
    for ex, info in exams.items():
        if info["max_total"]:
            info["percent"] = round(info["total_score"] * 100.0 / info["max_total"], 2)
            # Calculate grade based on percentage
            percent = info["percent"]
            if percent >= 90:
                info["grade"] = "A+"
            elif percent >= 80:
                info["grade"] = "A"
            elif percent >= 70:
                info["grade"] = "B"
            elif percent >= 60:
                info["grade"] = "C"
            elif percent >= 50:
                info["grade"] = "D"
            else:
                info["grade"] = "F"
        else:
            info["percent"] = None
            info["grade"] = "N/A"
        # Annotate each mark with per-subject percent and grade for template
        for m in info["marks"]:
            if m.max_score:
                subj_pct = round(m.score * 100.0 / m.max_score, 2)
            else:
                subj_pct = None
            # attach attributes to the model instance (safe for template use)
            setattr(m, "subject_percent", subj_pct)
            if subj_pct is None:
                setattr(m, "subject_grade", None)
            elif subj_pct >= 90:
                setattr(m, "subject_grade", "A+")
            elif subj_pct >= 80:
                setattr(m, "subject_grade", "A")
            elif subj_pct >= 70:
                setattr(m, "subject_grade", "B")
            elif subj_pct >= 60:
                setattr(m, "subject_grade", "C")
            elif subj_pct >= 50:
                setattr(m, "subject_grade", "D")
            else:
                setattr(m, "subject_grade", "F")

    context = {"student": student, "exams": exams}
    return render(request, "Students/results.html", context)


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def update_mark(request, student_id):
    student = get_object_or_404(Student, pk=student_id)
    user = request.user
    is_admin = _is_admin(user)

    initial_subject = request.GET.get("subject", "")
    initial_exam = request.GET.get("exam", "")

    if not initial_subject or not initial_exam:
        messages.error(request, "Subject and exam name are required.")
        return redirect("teacher_marks")

    # Additional validation: if the user is a non-admin teacher, ensure they
    # can only edit marks for students in their department and only for
    # subjects that belong to their department and are approved.
    if not is_admin:
        my_teacher = getattr(user, "teacher_profile", None)
        if not my_teacher or not getattr(my_teacher, "department", None):
            messages.error(request, "You are not assigned to a department.")
            return redirect("teacher_marks")

        # Ensure the student belongs to the teacher's department
        if getattr(student, "department", None) != my_teacher.department:
            messages.error(
                request, "You don't have permission to edit marks for this student."
            )
            return redirect("teacher_marks")

        # Validate the subject belongs to the teacher's department and is approved
        subject_obj = Subject.objects.filter(
            name=initial_subject, department=my_teacher.department, is_approved=True
        ).first()
        if not subject_obj:
            messages.error(
                request, "Invalid subject for your department or subject not approved."
            )
            return redirect("teacher_marks")

    existing = Mark.objects.filter(
        student=student, subject=initial_subject, exam_name=initial_exam
    ).first()

    if request.method == "POST":
        # For teachers, use TeacherMarkForm (only score and max_score)
        # For admins, use full MarkForm
        if is_admin:
            form = MarkForm(request.POST, instance=existing)
        else:
            form = TeacherMarkForm(request.POST, instance=existing)

        if form.is_valid():
            mark = form.save(commit=False)
            mark.student = student
            # Only set subject and exam_name if creating new mark (for teachers)
            if not existing:
                mark.subject = initial_subject
                mark.exam_name = initial_exam
            mark.updated_by = request.user
            mark.save()
            messages.success(request, "Marks updated successfully.")
            return redirect("teacher_marks")
        messages.error(request, "Please correct the errors below.")
    else:
        # Use TeacherMarkForm for teachers, MarkForm for admins
        if is_admin:
            form = MarkForm(instance=existing)
            if initial_subject:
                form.fields["subject"].initial = initial_subject
            if initial_exam:
                form.fields["exam_name"].initial = initial_exam
        else:
            form = TeacherMarkForm(instance=existing)

    context = {
        "student": student,
        "form": form,
        "subject": initial_subject,
        "exam_name": initial_exam,
        "is_admin": is_admin,
        "existing": existing is not None,
    }
    return render(request, "Students/update-mark.html", context)


@login_required
def teacher_details(request, pk):
    """View teacher details. Teachers can view own profile, admin can view all."""
    teacher = get_object_or_404(
        Teacher.objects.select_related("department", "user"), pk=pk
    )

    user = request.user
    is_admin = _is_admin(user)
    is_own_profile = (
        hasattr(user, "teacher_profile") and user.teacher_profile.pk == teacher.pk
    )

    if not (is_admin or is_own_profile or _is_teacher(user)):
        messages.error(
            request, "You don't have permission to view this teacher's profile."
        )
        return redirect("teacher_list")

    context = {"teacher": teacher, "is_admin": is_admin}
    return render(request, "Teachers/teacher-details.html", context)


@login_required
def teacher_list(request):
    # Select related to avoid extra queries for department and linked user
    teachers = Teacher.objects.select_related("department", "user").all()
    # If the current user is a teacher (and not admin), restrict the list
    # to teachers in the same department to match requested behavior.
    user = request.user
    is_teacher_user = (
        getattr(user, "is_authenticated", False)
        and getattr(user, "is_teacher", False)
        and not _is_admin(user)
    )
    current_department = None
    if is_teacher_user:
        my_teacher = getattr(user, "teacher_profile", None)
        if my_teacher and my_teacher.department:
            current_department = my_teacher.department
            teachers = teachers.filter(department=current_department)
        else:
            # Not assigned to a department -> show empty list
            teachers = Teacher.objects.none()

    # search query (kept for admins / developers but optional)
    search_query = request.GET.get("search", "")
    if search_query:
        teachers = teachers.filter(
            Q(first_name__icontains=search_query)
            | Q(last_name__icontains=search_query)
            | Q(teacher_id__icontains=search_query)
            | Q(email__icontains=search_query)
        )

    context = {
        "teacher_list": teachers,
        "is_admin": _is_admin(request.user),
        "is_teacher_user": is_teacher_user,
        "current_department": current_department,
    }
    return render(request, "Teachers/teachers.html", context)


@login_required
@user_passes_test(_is_admin)
def add_teacher(request):
    """Add new teacher (Admin only)"""
    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            teacher = form.save()
            messages.success(
                request,
                f"Teacher '{teacher.first_name} {teacher.last_name}' added successfully.",
            )
            return redirect("teacher_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherForm()

    context = {"form": form}
    return render(request, "Teachers/add-teacher.html", context)


@login_required
def edit_teacher(request, slug):
    """Edit teacher. Teachers can edit own profile, admin can edit all."""
    teacher = get_object_or_404(Teacher, slug=slug)

    # Check permissions
    user = request.user
    is_admin = _is_admin(user)
    is_own_profile = (
        hasattr(user, "teacher_profile") and user.teacher_profile.pk == teacher.pk
    )

    if not (is_admin or is_own_profile):
        messages.error(request, "You don't have permission to edit this teacher.")
        return redirect("teacher_list")

    if request.method == "POST":
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            teacher = form.save()
            messages.success(
                request,
                f"Teacher '{teacher.first_name} {teacher.last_name}' updated successfully.",
            )
            return redirect("teacher_list")
        messages.error(request, "Please correct the errors below.")
    else:
        form = TeacherForm(instance=teacher)

    context = {"form": form, "teacher": teacher, "is_admin": is_admin}
    return render(request, "Teachers/edit-teacher.html", context)


@login_required
@user_passes_test(_is_admin)
def delete_teacher(request, slug):
    """Delete teacher (Admin only)"""
    if request.method == "POST":
        teacher = get_object_or_404(Teacher, slug=slug)
        teacher_name = f"{teacher.first_name} {teacher.last_name}"
        teacher.delete()
        messages.success(request, f"Teacher '{teacher_name}' deleted successfully.")
        return redirect("teacher_list")
    return HttpResponseForbidden()


# ========== TEACHER OPERATIONS: MARKS, DEPARTMENTS, SUBJECTS ==========


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def teacher_marks(request):
    """Teacher view to see all students with all subjects and update marks."""
    user = request.user
    is_admin = _is_admin(user)

    # Get teacher profile and department for non-admin users
    my_teacher = None
    teacher_department = None
    if not is_admin:
        my_teacher = getattr(user, "teacher_profile", None)
        if my_teacher:
            teacher_department = my_teacher.department

    # Get students - filter by teacher's department if not admin
    if is_admin:
        students = (
            Student.objects.select_related("department")
            .all()
            .order_by("first_name", "last_name")
        )
        subjects = Subject.objects.filter(is_approved=True).order_by("name")
    else:
        # For teachers, only show students and subjects from their department
        if my_teacher and my_teacher.department:
            students = Student.objects.filter(
                department=my_teacher.department
            ).order_by("first_name", "last_name")
            subjects = Subject.objects.filter(
                department=my_teacher.department, is_approved=True
            ).order_by("name")
        else:
            students = Student.objects.none()
            subjects = Subject.objects.none()

    # Get all existing marks for these students
    existing_marks = Mark.objects.filter(student__in=students).select_related(
        "student", "updated_by"
    )

    # Create a dictionary for quick mark lookup: (student_id, subject_name, exam_name) -> mark
    marks_dict = {}
    for mark in existing_marks:
        key = (mark.student.pk, mark.subject, mark.exam_name)
        marks_dict[key] = mark

    # Build students_with_subjects: list of dicts with student and their subjects
    students_with_subjects = []
    for student in students:
        student_subjects = []
        for subject in subjects:
            # Get all marks for this student-subject combination
            subject_marks = []
            for mark in existing_marks:
                if mark.student.pk == student.pk and mark.subject == subject.name:
                    subject_marks.append(mark)
            student_subjects.append(
                {
                    "subject": subject,
                    "marks": sorted(subject_marks, key=lambda x: x.exam_name),
                }
            )
        students_with_subjects.append(
            {"student": student, "subjects": student_subjects}
        )

    context = {
        "students_with_subjects": students_with_subjects,
        "is_admin": is_admin,
        "teacher_department": teacher_department,
        "my_teacher": my_teacher,
    }
    return render(request, "Teachers/teacher-marks.html", context)


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def department_list(request):
    """List all departments."""
    departments = Department.objects.all().order_by("name")
    context = {"departments": departments}
    return render(request, "Teachers/department-list.html", context)


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def add_department(request):
    """Add a new department."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Department name is required.")
        else:
            try:
                dept = Department.objects.create(
                    name=name,
                    code=code if code else None,
                    description=description if description else "",
                )
                messages.success(
                    request, f"Department '{dept.name}' added successfully."
                )
                return redirect("department_list")
            except Exception as e:
                messages.error(request, f"Error creating department: {str(e)}")

    return render(request, "Teachers/add-department.html")


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def subject_list(request):
    """List all subjects."""
    subjects = Subject.objects.select_related("department").all().order_by("name")
    is_admin = _is_admin(request.user)

    # Get teacher profile and department for non-admin users
    my_teacher = None
    teacher_department = None
    if not is_admin:
        my_teacher = getattr(request.user, "teacher_profile", None)
        if my_teacher:
            teacher_department = my_teacher.department
            if teacher_department:
                subjects = subjects.filter(
                    department=teacher_department, is_approved=True
                )
            else:
                subjects = Subject.objects.none()

    context = {
        "subjects": subjects,
        "is_admin": is_admin,
        "teacher_department": teacher_department,
        "my_teacher": my_teacher,
    }
    return render(request, "Teachers/subject-list.html", context)


@login_required
@user_passes_test(lambda u: _is_teacher(u) or _is_admin(u))
def add_subject(request):
    """Add a new subject."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        department_id = request.POST.get("department", "").strip()
        description = request.POST.get("description", "").strip()

        if not name:
            messages.error(request, "Subject name is required.")
        else:
            try:
                department = None
                # If a department was posted, use it. Otherwise, if the current
                # user is a non-admin teacher, default the subject to the
                # teacher's department so it is visible to them after creation.
                if department_id:
                    department = Department.objects.filter(pk=department_id).first()
                else:
                    # try to default to the teacher's department for non-admins
                    user = request.user
                    if (
                        getattr(user, "is_authenticated", False)
                        and getattr(user, "is_teacher", False)
                        and not _is_admin(user)
                    ):
                        my_teacher = getattr(user, "teacher_profile", None)
                        if my_teacher and my_teacher.department:
                            department = my_teacher.department

                # Decide approval status: admin-created subjects are
                # approved immediately; subjects created by ordinary
                # teachers should require admin approval.
                is_approved_flag = True
                current_user = request.user
                if (
                    getattr(current_user, "is_authenticated", False)
                    and getattr(current_user, "is_teacher", False)
                    and not _is_admin(current_user)
                ):
                    is_approved_flag = False

                subject = Subject.objects.create(
                    name=name,
                    code=code if code else None,
                    department=department,
                    description=description if description else "",
                    is_approved=is_approved_flag,
                )

                if is_approved_flag:
                    messages.success(
                        request, f"Subject '{subject.name}' added successfully."
                    )
                else:
                    messages.info(
                        request, "Subject submitted and is waiting for admin approval."
                    )

                return redirect("subject_list")
            except Exception as e:
                messages.error(request, f"Error creating subject: {str(e)}")

    departments = Department.objects.all().order_by("name")
    context = {"departments": departments}
    return render(request, "Teachers/add-subject.html", context)


def _is_teacher(user):
    return getattr(user, "is_teacher", False) or user.is_superuser


@login_required
@user_passes_test(_is_teacher)
def teachers_in_department(request):
    """List teachers in the same department as the logged-in teacher."""
    teacher = getattr(request.user, "teacher_profile", None)
    if not teacher or not teacher.department:
        messages.info(request, "You are not assigned to a department.")
        # Option: show empty list or redirect
        return render(
            request, "Teachers/teacher_list_department.html", {"teacher_list": []}
        )

    dept = teacher.department
    teacher_list = Teacher.objects.filter(department=dept).order_by(
        "first_name", "last_name"
    )
    return render(
        request,
        "Teachers/teacher_list_department.html",
        {"teacher_list": teacher_list, "department": dept},
    )


@login_required
def teacher_detail(request, slug):
    """Show teacher details — allow view only if same department or superuser."""
    t = get_object_or_404(Teacher, slug=slug)
    # Allow if superuser, same department, or the teacher themself
    if request.user.is_superuser:
        allowed = True
    else:
        my_teacher = getattr(request.user, "teacher_profile", None)
        allowed = (
            my_teacher is not None and my_teacher.department == t.department
        ) or (
            getattr(request.user, "teacher_profile", None)
            and t == request.user.teacher_profile
        )
    if not allowed:
        return HttpResponseForbidden("You are not allowed to view this teacher.")
    # Use the hyphenated template filename that exists in templates/Teachers/
    return render(request, "Teachers/teacher-details.html", {"teacher": t})


@login_required
@user_passes_test(_is_teacher)
def create_assignment(request, slug=None):
    """
    Create an assignment and assign it to students.
    If slug provided, use that teacher's department to pre-filter students.
    Otherwise use the current teacher's department.
    """
    my_teacher = getattr(request.user, "teacher_profile", None)
    if not my_teacher and not request.user.is_superuser:
        return HttpResponseForbidden("Only teachers can create assignments.")

    # determine department to restrict student choices
    if slug:
        teacher_obj = get_object_or_404(Teacher, slug=slug)
        department = teacher_obj.department
    else:
        department = getattr(my_teacher, "department", None)

    if request.method == "POST":
        form = AssignmentForm(request.POST)
        assign_form = AssignmentAssignForm(request.POST)
        # set the queryset for students dynamically
        if department:
            assign_form.fields["students"].queryset = Student.objects.filter(
                student_class__isnull=False,  # optional
            ).filter(
                # choose filter: by department if Student has department link; if not, you may use student_class/section mapping
                # For this project, we'll assume Student doesn't have department; adjust as needed.
                # If Student has department FK, use: Student.objects.filter(department=department)
                # Here we filter by a placeholder, change to your schema.
            )
        else:
            assign_form.fields["students"].queryset = Student.objects.none()

        if form.is_valid() and assign_form.is_valid():
            assignment = form.save(commit=False)
            assignment.created_by = request.user
            assignment.department = department
            assignment.save()
            assignment.assigned_students.set(assign_form.cleaned_data["students"])
            messages.success(request, "Assignment created and students assigned.")
            return redirect("teacher_dashboard")
    else:
        form = AssignmentForm()
        assign_form = AssignmentAssignForm()
        if department:
            # If Student model had department FK: Student.objects.filter(department=department)
            # Here we try Student.objects.filter(student_class=...) but adjust according to your schema.
            # Best is: Student.objects.filter(department=department)
            try:
                assign_form.fields["students"].queryset = Student.objects.filter(
                    department=department
                )
            except Exception:
                assign_form.fields["students"].queryset = Student.objects.none()

    return render(
        request,
        "Teachers/assignment_create.html",
        {
            "form": form,
            "assign_form": assign_form,
            "department": department,
        },
    )


@login_required
def my_assignments(request):
    """List assignments assigned to the logged-in student."""
    if not getattr(request.user, "is_student", False):
        return HttpResponseForbidden("Only students can view their assignments.")

    student = getattr(request.user, "student_profile", None)
    if not student:
        messages.error(request, "No student profile linked to your account.")
        return redirect("student_dashboard")

    assignments = student.assignments.all().order_by("-created_at")
    return render(request, "Students/my_assignments.html", {"assignments": assignments})
