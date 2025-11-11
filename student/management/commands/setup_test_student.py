"""
Django management command to set up test student data for testing the results feature.
Usage: python manage.py setup_test_student
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from student.models import Student, Mark

# Get the user model (will be CustomUser based on AUTH_USER_MODEL setting)
User = get_user_model()


class Command(BaseCommand):
    help = "Creates a test student with sample marks for testing the results feature"

    def handle(self, *args, **options):
        # Create or get user
        username = "student1"
        password = "test123"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={"email": "student1@gmail.com", "is_student": True},
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ User "{username}" created!'))
        else:
            # Update user to be a student if not already
            if hasattr(user, "is_student") and not user.is_student:
                user.is_student = True
                user.save()
            self.stdout.write(self.style.WARNING(f'User "{username}" already exists.'))

        # Create or get student
        student, created = Student.objects.get_or_create(
            student_id="STU001",
            defaults={
                "first_name": "John",
                "last_name": "Doe",
                "gender": "Male",
                "student_class": "Grade 10",
                "admission_number": "STU001",
                "section": "A",
                "user": user,
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("✓ Student created!"))
        else:
            # Always ensure user is linked to student (even if student already exists)
            if not student.user or student.user != user:
                student.user = user
                student.save()
                self.stdout.write(self.style.SUCCESS("✓ Student linked to user!"))
            else:
                self.stdout.write(
                    self.style.WARNING("Student already exists and is linked.")
                )

        # Add sample marks
        marks_data = [
            {
                "subject": "Mathematics",
                "exam_name": "Midterm Exam 2024",
                "score": 85,
                "max_score": 100,
            },
            {
                "subject": "Science",
                "exam_name": "Midterm Exam 2024",
                "score": 92,
                "max_score": 100,
            },
            {
                "subject": "English",
                "exam_name": "Midterm Exam 2024",
                "score": 78,
                "max_score": 100,
            },
            {
                "subject": "History",
                "exam_name": "Midterm Exam 2024",
                "score": 88,
                "max_score": 100,
            },
            {
                "subject": "Mathematics",
                "exam_name": "Final Exam 2024",
                "score": 88,
                "max_score": 100,
            },
            {
                "subject": "Science",
                "exam_name": "Final Exam 2024",
                "score": 95,
                "max_score": 100,
            },
            {
                "subject": "English",
                "exam_name": "Final Exam 2024",
                "score": 82,
                "max_score": 100,
            },
            {
                "subject": "History",
                "exam_name": "Final Exam 2024",
                "score": 90,
                "max_score": 100,
            },
        ]

        marks_created = 0
        for mark_data in marks_data:
            mark, created = Mark.objects.get_or_create(
                student=student,
                subject=mark_data["subject"],
                exam_name=mark_data["exam_name"],
                defaults={
                    "score": mark_data["score"],
                    "max_score": mark_data["max_score"],
                },
            )
            if created:
                marks_created += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✓ Mark added: {mark_data["subject"]} - {mark_data["exam_name"]} '
                        f'({mark_data["score"]}/{mark_data["max_score"]})'
                    )
                )

        if marks_created == 0:
            self.stdout.write(self.style.WARNING("All marks already exist."))

        # Verify the link is working
        self.stdout.write("")
        self.stdout.write("Verifying user-student link...")
        user.refresh_from_db()
        student.refresh_from_db()

        if hasattr(user, "student_profile") and user.student_profile == student:
            self.stdout.write(self.style.SUCCESS("✓ User-student link verified!"))
        elif student.user == user:
            self.stdout.write(self.style.SUCCESS("✓ User-student link verified!"))
        else:
            self.stdout.write(
                self.style.WARNING(
                    "✗ Warning: User-student link may not be working correctly."
                )
            )
            self.stdout.write(self.style.WARNING("  User: %s" % user))
            self.stdout.write(self.style.WARNING("  Student: %s" % student))
            self.stdout.write(self.style.WARNING("  Student.user: %s" % student.user))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("✅ Test data setup complete!"))
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write(f"  Username: {username}")
        self.stdout.write(f"  Email: {user.email}")
        self.stdout.write(f"  Password: {password}")
        self.stdout.write("")
        self.stdout.write("Student Info:")
        self.stdout.write(f"  Name: {student.first_name} {student.last_name}")
        self.stdout.write(f"  Student ID: {student.student_id}")
        self.stdout.write(f"  Admission Number: {student.admission_number}")
        self.stdout.write(f"  Class: {student.student_class}")
        self.stdout.write("")
        self.stdout.write("Test URLs:")
        self.stdout.write(
            "  1. Student Dashboard: http://127.0.0.1:8000/student/dashboard/"
        )
        self.stdout.write(
            "  2. Student Results: http://127.0.0.1:8000/student/results/"
        )
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
