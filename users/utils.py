from django.conf import settings
from django.core.mail import send_mail

def send_activation_email(user):
    activation_link = f"{settings.BASE_URL}/activate{user.activation_token}"
    subject = "Activate your account"
    message = f"Hi {user.full_name},\n\nPlease click the following link to activate your account:\n{activation_link}"
    print(message)
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)