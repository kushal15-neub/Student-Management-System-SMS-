from urllib import request
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from .models import Parent, Student, Mark
from .forms import MarkForm


# Restored minimal student views so `student.urls` can import them.
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
        )
        messages.success(request, "Student added successfully.")
        # After creating a student redirect to the student list so the user
        # sees the newly added record. The template for the list is
        # `Students/students.html` and the named URL is `student_list`.
        return redirect("student_list")

    # Render the add form on GET (or if POST processing failed).
    return render(request, "Students/add-student.html")


def student_details(request, pk):
    """Render a student's detail page with data from database."""
    student = get_object_or_404(Student.objects.select_related("parent"), pk=pk)
    # Get all marks for this student
    marks = student.marks.all().order_by("exam_name", "subject")
    context = {"student": student, "marks": marks}
    return render(request, "Students/student-details.html", context)


def student_list(request):
    """Render the student listing page with data from database."""
    students = Student.objects.select_related("parent").all()
    context = {"student_list": students}
    return render(request, "Students/students.html", context)


def edit_student(request, pk):

    student = get_object_or_404(Student.objects.select_related("parent"), pk=pk)
    parent = student.parent

    if request.method == "POST":
        # Student fields
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

        # Update student fields
        student.first_name = first_name or student.first_name
        student.last_name = last_name or student.last_name
        student.student_id = student_id or student.student_id
        student.gender = gender or student.gender
        student.date_of_birth = date_of_birth or student.date_of_birth
        student.student_class = student_class or student.student_class
        student.religion = religion or student.religion
        student.joining_date = joining_date or student.joining_date
        student.mobile_number = mobile_number or student.mobile_number
        student.admission_number = admission_number or student.admission_number
        student.section = section or student.section
        if student_image:
            student.student_image = student_image
        student.parent = parent
        student.save()

        messages.success(request, "Student updated successfully.")
        return redirect("student_details", pk=student.pk)

    # GET -> render form
    context = {"student": student, "parent": parent}
    return render(request, "Students/edit-student.html", context)


@login_required
def student_dashboard(request):
    """Render the student dashboard page."""
    # Try to find the Student linked to the current user
    student = getattr(request.user, "student_profile", None)
    if student is None:
        # No direct link found — try a fallback by admission_number == username
        student = Student.objects.filter(admission_number=request.user.username).first()

    context = {"student": student}
    return render(request, "Students/student-dashboard.html", context)


@csrf_exempt
def public_results(request):
    """Public (unauthenticated) entry to view results by admission number.

    WARNING: This endpoint is intentionally permissive to allow previewing
    results before authentication is implemented. It should be considered
    temporary — prefer a token-based or authenticated flow in production.
    The view accepts POST with `admission_number` and optional
    `date_of_birth` (YYYY-MM-DD) to reduce accidental exposure.
    """
    student = None
    exams = {}

    if request.method == "POST":
        admission = request.POST.get("admission_number", "").strip()
        dob = request.POST.get("date_of_birth", "").strip()

        if not admission:
            messages.error(request, "Please provide an admission number.")
            return render(
                request,
                "Students/public_results_form.html",
                {"student": None, "exams": {}},
            )

        qs = Student.objects.filter(admission_number=admission)

        if dob:
            try:
                from datetime import datetime

                # HTML5 date input sends YYYY-MM-DD format, which is what we need
                dob_parsed = datetime.strptime(dob, "%Y-%m-%d").date()
                qs = qs.filter(date_of_birth=dob_parsed)
            except ValueError:
                messages.error(
                    request, "Invalid date format. Please use YYYY-MM-DD format."
                )
                return render(
                    request,
                    "Students/public_results_form.html",
                    {"student": None, "exams": {}},
                )
            except Exception as e:
                messages.error(request, f"Error processing date: {str(e)}")
                return render(
                    request,
                    "Students/public_results_form.html",
                    {"student": None, "exams": {}},
                )

        student = qs.first()
        if not student:
            messages.error(
                request,
                f"No student found with admission number: {admission}. Please check and try again.",
            )
            return render(
                request,
                "Students/public_results_form.html",
                {"student": None, "exams": {}},
            )

        # Build exams grouping and annotate marks (same format as student_results)
        marks = student.marks.all().order_by("exam_name", "subject")

        if not marks.exists():
            messages.warning(
                request,
                f"Student found, but no marks/results are available yet for {student.first_name} {student.last_name}.",
            )
            context = {"student": student, "exams": {}}
            return render(request, "Students/results.html", context)

        for m in marks:
            ex = m.exam_name
            exams.setdefault(ex, {"marks": [], "total_score": 0, "max_total": 0})
            exams[ex]["marks"].append(m)
            exams[ex]["total_score"] += m.score
            exams[ex]["max_total"] += m.max_score

        # Compute percent per exam and grade
        for ex, info in exams.items():
            if info["max_total"]:
                info["percent"] = round(
                    info["total_score"] * 100.0 / info["max_total"], 2
                )
                p = info["percent"]
                if p >= 90:
                    info["grade"] = "A+"
                elif p >= 80:
                    info["grade"] = "A"
                elif p >= 70:
                    info["grade"] = "B"
                elif p >= 60:
                    info["grade"] = "C"
                elif p >= 50:
                    info["grade"] = "D"
                else:
                    info["grade"] = "F"
            else:
                info["percent"] = None
                info["grade"] = "N/A"

            # Calculate subject-wise percentages and grades
            for m in info["marks"]:
                if m.max_score:
                    subj_pct = round(m.score * 100.0 / m.max_score, 2)
                else:
                    subj_pct = None
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

    # GET -> show the public form
    return render(
        request, "Students/public_results_form.html", {"student": None, "exams": {}}
    )


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
