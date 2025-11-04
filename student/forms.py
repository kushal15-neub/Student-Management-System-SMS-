from django import forms
from .models import Mark


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
