from django.contrib import admin
from .models import Parent, Student


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    # Use the actual model field names (avoid typos like `mothers_name`)
    list_display = ("father_name", "mother_name", "father_mobile", "mother_mobile")
    search_fields = ("father_name", "mother_name", "father_mobile", "mother_mobile")
    list_filter = ("father_name", "mother_name")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "first_name",
        "last_name",
        "student_id",
        "gender",
        "date_of_birth",
        "student_class",
        "joining_date",
        "section",
        "mobile_number",
    )

    search_fields = ("first_name", "last_name", "student_id", "mobile_number")
    list_filter = ("gender", "student_class", "section")
    readonly_fields = ("student_image",)
