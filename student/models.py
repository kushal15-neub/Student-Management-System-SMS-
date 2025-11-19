from pyclbr import Class
from django.db import models
from django.utils.text import slugify
from django.conf import settings


# Create your models here.
class Parent(models.Model):
    father_name = models.CharField(max_length=100)
    father_occupation = models.CharField(max_length=100)
    father_mobile = models.CharField(max_length=15)
    father_email = models.EmailField(max_length=100)
    mother_name = models.CharField(max_length=100)
    mother_occupation = models.CharField(max_length=100)
    mother_mobile = models.CharField(max_length=15)
    mother_email = models.EmailField(max_length=100)
    present_address = models.TextField()

    def __str__(self):
        return f"{self.father_name} & {self.mother_name}"


class Student(models.Model):
    # Optional link to a Django user so a Student can log in and view their
    # own results. This is nullable to avoid forcing an immediate backfill.
    # When present you can access the Student from a user with `request.user.student`.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="student_profile",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    student_id = models.CharField(max_length=100)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    student_class = models.CharField(max_length=100)
    religion = models.CharField(max_length=100, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    admission_number = models.CharField(max_length=15, blank=True)
    section = models.CharField(max_length=15, blank=True)
    student_image = models.ImageField(upload_to="student/", blank=True, null=True)

    # Link student to a Department so teachers can filter students by department.
    department = models.ForeignKey(
        "Department",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
    )

    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="students", null=True, blank=True
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        created = self.pk is None

        # For new objects, save first to get a PK
        if created:
            super().save(*args, **kwargs)

        # Generate slug if missing
        if not self.slug:
            identifier = self.student_id or str(self.pk)
            base = slugify(f"{self.first_name}-{identifier}") or "student"
            slug = base
            counter = 1

            while Student.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
            # If slug was missing, save again with just the slug field
            super().save(update_fields=["slug"])
        else:
            # For existing objects, always save to persist all field changes
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Mark(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="marks")
    subject = models.CharField(max_length=100)
    exam_name = models.CharField(max_length=100)
    score = models.PositiveIntegerField()
    max_score = models.PositiveIntegerField(default=100)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_marks",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "subject", "exam_name")
        ordering = ["student", "subject", "exam_name"]

    def __str__(self):
        return f"{self.student} - {self.subject} ({self.exam_name})"


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects",
    )
    description = models.TextField(blank=True)
    # Whether an admin has approved this subject. Default True keeps
    # existing subjects visible; new teacher-submitted subjects will be set
    # to False until an admin approves them.
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})" if self.code else self.name


class Course(models.Model):
    title = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True)
    subjects = models.ManyToManyField(Subject, related_name="courses", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.code})"


class Teacher(models.Model):
    # Optional link to a Django user so a Teacher can log in and view their
    # own classes and students. This is nullable to avoid forcing an immediate backfill.
    # When present you can access the Teacher from a user with `request.user.teacher_profile`.
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="teacher_profile",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    teacher_id = models.CharField(max_length=100, unique=True)
    gender = models.CharField(
        max_length=10,
        choices=[("Male", "Male"), ("Female", "Female"), ("Other", "Other")],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=255, unique=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers",
    )
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)
    teacher_image = models.ImageField(upload_to="teacher/", blank=True, null=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        created = self.pk is None

        # For new objects, save first to get a PK
        if created:
            super().save(*args, **kwargs)

        # Generate slug if missing
        if not self.slug:
            identifier = self.teacher_id or str(self.pk)
            base = slugify(f"{self.first_name}-{identifier}") or "teacher"
            slug = base
            counter = 1

            while Teacher.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
            super().save(update_fields=["slug"])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["first_name", "last_name"]


class Assignment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_assignments",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments",
    )

    assigned_students = models.ManyToManyField(
        Student, related_name="assignments", blank=True
    )

    due_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
