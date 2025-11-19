from django import forms
from .models import Mark
from .models import Assignment, Student


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ["subject", "exam_name", "score", "max_score"]

    def clean(self):
        cleaned = super().clean()
        score = cleaned.get("score")
        max_score = cleaned.get("max_score")
        if score is not None and max_score is not None and score > max_score:
            self.add_error("score", "Score cannot exceed Max score.")
        return cleaned


class TeacherMarkForm(forms.ModelForm):
    """Form for teachers to update only marks (score and max_score), not subject or exam."""

    class Meta:
        model = Mark
        fields = ["score", "max_score"]
        labels = {
            "score": "Score",
            "max_score": "Max Score",
        }

    def clean(self):
        cleaned = super().clean()
        score = cleaned.get("score")
        max_score = cleaned.get("max_score")
        if score is not None and max_score is not None and score > max_score:
            self.add_error("score", "Score cannot exceed Max score.")
        return cleaned


from .models import Teacher, Department, Subject


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            "user",
            "first_name",
            "last_name",
            "teacher_id",
            "gender",
            "date_of_birth",
            "email",
            "mobile_number",
            "joining_date",
            "department",
            "subjects",
            "teacher_image",
        ]
        widgets = {
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "subjects": forms.CheckboxSelectMultiple(),
            "user": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit choices to available department/subjects
        self.fields["department"].queryset = Department.objects.all()
        self.fields["subjects"].queryset = Subject.objects.all()
        # User field - show only users who are teachers but don't have a teacher profile yet
        from home_auth.models import CustomUser

        users_with_teacher_profile = Teacher.objects.exclude(
            user__isnull=True
        ).values_list("user_id", flat=True)
        self.fields["user"].queryset = CustomUser.objects.filter(
            is_teacher=True
        ).exclude(id__in=users_with_teacher_profile)
        self.fields["user"].required = False
        self.fields["user"].help_text = (
            "Optional: Link to an existing user account (select a user with is_teacher=True)"
        )


class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ["title", "description", "due_date"]


class AssignmentAssignForm(forms.Form):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign to students",
    )
