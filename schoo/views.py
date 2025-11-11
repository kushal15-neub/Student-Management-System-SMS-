from django.shortcuts import render, redirect
from django.http import HttpResponse


# Create your views here.
def index(request):
    # If already authenticated, send users to their dashboard instead of login
    if request.user.is_authenticated:
        # For now, route everyone to the student dashboard (adjust if needed)
        return redirect("student_dashboard")
    return render(request, "authentication/login.html")


def dashboard(request):
    return render(request, "student/student-dashboard.html")
