from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from .forms import ProfileForm
import re


def signup_view(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        role = request.POST.get("role")  # student | teacher | admin

        # Validate role
        allowed_roles = {"student", "teacher", "admin"}
        if not role or role not in allowed_roles:
            messages.error(
                request, "Please select a valid role: student, teacher or admin."
            )
            return render(request, "authentication/register.html")
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "authentication/register.html")
        if not email:
            messages.error(request, "Email is required.")
            return render(request, "authentication/register.html")
        # Enforce only gmail.com addresses
        if not email.lower().endswith("@gmail.com"):
            messages.error(request, "Only @gmail.com addresses are accepted.")
            return render(request, "authentication/register.html")
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "authentication/register.html")

        # Validate first and last name: reject names that contain digits or
        # invalid characters. Allow letters, spaces, hyphens and apostrophes.
        def valid_name(n):
            if not n or len(n) < 2:
                return False
            # disallow digits anywhere
            if any(c.isdigit() for c in n):
                return False
            # only allow letters, spaces, hyphen and apostrophe
            if not re.match(r"^[A-Za-z\s'\-]+$", n):
                return False
            return True

        if not valid_name(first_name):
            messages.error(request, "Please enter a valid first name (letters only).")
            return render(request, "authentication/register.html")
        if not valid_name(last_name):
            messages.error(request, "Please enter a valid last name (letters only).")
            return render(request, "authentication/register.html")

        # Create the user
        user = CustomUser.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )

        # Assign the appropriate role flags (safe assignment)
        try:
            user.is_student = role == "student"
            user.is_teacher = role == "teacher"
            if role == "admin":
                user.is_admin = True
                user.is_staff = True
                user.is_superuser = True
        except Exception:
            # If the CustomUser doesn't have those fields, ignore silently
            pass

        user.save()  # Save the user with the assigned role
        # If the user signed up as a teacher, create a Teacher profile linked
        # to this user. The teacher record will be created without a
        # department so the superadmin can assign it later via admin. We
        # generate a simple teacher_id based on the user PK to ensure
        # uniqueness.
        try:
            if role == "teacher":
                from Home.student.models import Teacher

                # Use a temporary teacher_id; will be unique because user.pk exists
                teacher_id = f"T{user.pk}"
                Teacher.objects.create(
                    user=user,
                    first_name=first_name,
                    last_name=last_name,
                    teacher_id=teacher_id,
                    email=email,
                )
        except Exception:
            # Don't block signup if creating Teacher profile fails; log could be added
            pass
        login(request, user)
        messages.success(request, "Signup successful!")
        return redirect("index")  # Redirect to the index or home page
    return render(request, "authentication/register.html")  # Render signup template


def login_view(request):
    next_url = request.GET.get("next") or request.POST.get("next")
    # If already authenticated, avoid showing login again
    if request.user.is_authenticated:
        return redirect("student_dashboard")
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")

            # Honor ?next=... first if provided
            if next_url:
                return redirect(next_url)

            # Redirect user based on their role to existing routes
            if user.is_superuser or user.is_admin:
                return redirect("admin:index")
            elif user.is_teacher:
                return redirect("teacher_dashboard")
            elif user.is_student:
                return redirect("student_dashboard")
            else:
                messages.error(request, "Invalid user role")
                return redirect("index")  # Redirect to index in case of error

        else:
            messages.error(request, "Invalid credentials")
    return render(
        request, "authentication/login.html", {"next": next_url}
    )  # Render login template


def forgot_password_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        user = CustomUser.objects.filter(email=email).first()

        if user:
            # Invalidate any previous reset tokens for this user
            PasswordResetRequest.objects.filter(user=user).delete()
            token = get_random_string(32)
            reset_request = PasswordResetRequest.objects.create(
                user=user, email=email, token=token
            )
            reset_request.send_reset_email()
            messages.success(request, "Reset link sent to your email.")
        else:
            messages.error(request, "Email not found.")

    return render(
        request, "authentication/forgot-password.html"
    )  # Render forgot password template


def reset_password_view(request, token):
    reset_request = PasswordResetRequest.objects.filter(token=token).first()

    if not reset_request or not reset_request.is_valid():
        messages.error(request, "Invalid or expired reset link")
        return redirect("index")

    if request.method == "POST":
        new_password = request.POST.get("new_password", "")
        confirm_password = request.POST.get("confirm_password", "")
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(
                request, "authentication/reset_password.html", {"token": token}
            )
        reset_request.user.set_password(new_password)
        reset_request.user.save()
        # Invalidate the token after successful reset
        reset_request.delete()
        messages.success(request, "Password reset successful")
        return redirect("login")

    return render(
        request, "authentication/reset_password.html", {"token": token}
    )  # Render reset password template


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")


@login_required
def profile_view(request):
    """Render and handle profile edit (including avatar upload)."""
    user = request.user

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=user)

    # Get teacher profile if user is a teacher
    teacher_profile = None
    if hasattr(user, "teacher_profile"):
        teacher_profile = user.teacher_profile

    context = {
        "form": form,
        "teacher_profile": teacher_profile,
    }
    return render(request, "authentication/profile.html", context)
