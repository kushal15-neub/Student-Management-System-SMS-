"""
Django management command to set up test student data for testing the results feature.
Usage: python manage.py setup_test_student
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from student.models import Student, Mark


class Command(BaseCommand):
    help = "Creates a test student with sample marks for testing the results feature"

    def handle(self, *args, **options):
        # Create or get user
        username = "student1"
        password = "test123"

        user, created = User.objects.get_or_create(
            username=username, defaults={"email": "student1@example.com"}
        )
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'✓ User "{username}" created!'))
        else:
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
            # Update user link if student exists but user is not linked
            if not student.user:
                student.user = user
                student.save()
                self.stdout.write(self.style.SUCCESS("✓ Student linked to user!"))
            else:
                self.stdout.write(self.style.WARNING("Student already exists."))

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

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=" * 60))
        self.stdout.write(self.style.SUCCESS("✅ Test data setup complete!"))
        self.stdout.write("")
        self.stdout.write("Login credentials:")
        self.stdout.write(f"  Username: {username}")
        self.stdout.write(f"  Password: {password}")
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
