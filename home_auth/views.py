from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import CustomUser, PasswordResetRequest
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string


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
