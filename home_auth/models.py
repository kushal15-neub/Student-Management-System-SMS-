from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail, get_connection, EmailMessage
import logging
from django.conf import settings
from django.utils.crypto import get_random_string
from django.utils import timezone


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=255, unique=True, db_index=True)
    is_authorized = models.BooleanField(default=False)
    login_token = models.CharField(max_length=6, blank=True, null=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    # Fields for user roles
    is_student = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)

    # Optional avatar for user profile
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    # Override groups and user_permissions to avoid conflicts
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    def __str__(self):
        return self.username


class PasswordResetRequest(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(
        max_length=32, default=get_random_string(32), editable=False, unique=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # Define token validity period (e.g., 1 hour)
    TOKEN_VALIDITY_PERIOD = timezone.timedelta(hours=1)

    def is_valid(self):
        return timezone.now() <= self.created_at + self.TOKEN_VALIDITY_PERIOD

    def send_reset_email(self):
        reset_link = (
            f"http://localhost:8000/authentication/reset-password/{self.token}/"
        )
        subject = "Password Reset Request"
        body = f"Click the following link to reset your password: {reset_link}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to = [self.email]

        logger = logging.getLogger(__name__)

        try:
            # Use configured email backend first
            send_mail(subject, body, from_email, to, fail_silently=False)
        except Exception as exc:
            # Log the failure with stack trace
            logger.exception("Failed to send password reset email: %s", exc)

            # Check if it's an authentication error and provide helpful message
            error_str = str(exc)
            if (
                "BadCredentials" in error_str
                or "535" in error_str
                or "Username and Password not accepted" in error_str
            ):
                logger.error(
                    "Gmail SMTP authentication failed. "
                    "Please ensure you're using an App Password (not your regular Gmail password). "
                    "To generate an App Password: "
                    "1. Enable 2-Step Verification on your Google account "
                    "2. Go to https://myaccount.google.com/apppasswords "
                    "3. Generate an App Password for 'Mail' "
                    "4. Set EMAIL_HOST_PASSWORD environment variable to the App Password"
                )

            # In DEBUG/development, fallback to the console backend so the
            # application doesn't raise a 500 and developers can still see
            # the reset link in the runserver output.
            if getattr(settings, "DEBUG", False):
                try:
                    conn = get_connection(
                        backend="django.core.mail.backends.console.EmailBackend"
                    )
                    EmailMessage(subject, body, from_email, to, connection=conn).send()
                    logger.info(
                        "Password reset email written to console backend as fallback."
                    )
                except Exception:
                    logger.exception("Console backend also failed to send reset email.")
            # Do not re-raise: swallow to avoid a 500 in the user-facing flow.
            return False

        return True
