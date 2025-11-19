from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import CustomUser
from django.contrib import admin as dj_admin
from django.apps import apps


# Register your models here.


# Custom UserAdmin with conditional logic for superusers and staff
class CustomUserAdmin(DefaultUserAdmin):
    # Customize which fields are displayed in the admin form
    fieldsets = (
        (None, {"fields": ("username", "password")}),  # Login details
        (
            "Personal info",
            {"fields": ("first_name", "last_name", "email")},
        ),  # Personal details
        ("Roles", {"fields": ("is_student", "is_teacher", "is_admin")}),  # Role fields
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_authorized",  # Add is_authorized here
                    "groups",
                    "user_permissions",
                )
            },
        ),  # Admin permissions
    )

    # Customize fields in the user creation form (when creating a new user)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_authorized",
                    "is_student",
                    "is_teacher",
                    "is_admin",
                ),
            },
        ),
    )

    # Customize what fields are displayed in the list view
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_authorized",
        "is_student",
        "is_teacher",
        "is_admin",
        "is_staff",
        "is_superuser",
    )

    # Filter users based on role and authorization
    list_filter = (
        "is_student",
        "is_teacher",
        "is_admin",
        "is_authorized",
        "is_staff",
        "is_superuser",
    )

    # Customize queryset to separate superusers and staff in the admin list view
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset  # Superusers see all users
        return queryset.filter(
            is_superuser=False
        )  # Non-superuser staff won't see superusers

    def get_inline_instances(self, request, obj=None):
        # Attach Teacher inline so admins can edit teacher profile from user admin
        inlines = super().get_inline_instances(request, obj)
        if obj is not None:
            try:
                # Get Teacher model dynamically to avoid import-time issues
                Teacher = apps.get_model("student", "Teacher")
                InlineCls = type(
                    "TeacherInline",
                    (dj_admin.StackedInline,),
                    {
                        "model": Teacher,
                        "can_delete": False,
                        "fk_name": "user",
                        "fields": (
                            "first_name",
                            "last_name",
                            "teacher_id",
                            "department",
                            "email",
                        ),
                        "extra": 0,
                    },
                )
                inline = InlineCls(self.model, self.admin_site)
                inlines.append(inline)
            except Exception:
                # If the student app or Teacher model is not available, skip inline
                pass
        return inlines


# Register the CustomUser model with the custom admin
admin.site.register(CustomUser, CustomUserAdmin)
