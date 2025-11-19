from django.contrib import admin
from .models import Parent, Student, Mark, Department, Subject, Course, Teacher

admin.site.register(Teacher)


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


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "subject",
        "exam_name",
        "score",
        "max_score",
        "updated_at",
    )
    list_filter = ("subject", "exam_name")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__student_id",
        "subject",
        "exam_name",
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")
    list_filter = ("created_at",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "department", "is_approved", "created_at")
    search_fields = ("name", "code", "description")
    list_filter = ("department", "is_approved", "created_at")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "is_active", "created_at")
    search_fields = ("title", "code", "description")
    list_filter = ("is_active", "subjects", "created_at")
    filter_horizontal = ("subjects",)
