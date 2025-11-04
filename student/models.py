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

    
    parent = models.ForeignKey(
        Parent, on_delete=models.CASCADE, related_name="students", null=True, blank=True
    )
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
       
        created = self.pk is None
        if created:
      
            super().save(*args, **kwargs)

        if not self.slug:
            identifier = self.student_id or str(self.pk)
            base = slugify(f"{self.first_name}-{identifier}") or "student"
            slug = base
            counter = 1
          
            while Student.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
            super().save(update_fields=["slug"])
        else:
            # If slug already provided and object was created above, ensure other fields are saved
            if created:
                super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Mark(models.Model):
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="marks"
    )
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
