from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.urls import reverse
from django.db.models.signals import post_save
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django_rest_passwordreset.signals import reset_password_token_created
from django.utils import timezone
from users.models import CustomUser, CustomerProfile, LoginLog, AdminProfile



@receiver(user_logged_in)
def log_user_logged_in(sender, request, user, **kwargs):
    if user.is_staff:
        login_log = LoginLog.objects.create(user=user, login_location=request.META.get('REMOTE_ADDR'))
        login_log.save()
        print("User Logged in")

@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    username = credentials.get('username')
    if username:
        try:
            user = CustomUser.objects.get(username=username)
            if user.is_staff:
                login_log = LoginLog.objects.create(user=user, login_failed=True, login_location=request.META.get('REMOTE_ADDR'))
                login_log.save()
        except CustomUser.DoesNotExist:
            pass
    print("User Login failed")


@receiver(user_logged_out)
def log_user_logged_out(sender, request, user, **kwargs):
    if user.is_staff:
        try:
            login_log = LoginLog.objects.filter(user=user).latest('login_time')
            login_log.logout_time = timezone.now()
            login_log.save()
        except LoginLog.DoesNotExist:
            pass
    print("User Logged out")
    
    
@receiver(post_save, sender=CustomUser)
def create_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            AdminProfile.objects.create(user=instance)
        else:
            CustomerProfile.objects.create(user=instance)

    
    
@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'reset_password_url': "{}?token={}".format(
            instance.request.build_absolute_uri(reverse('password_reset:reset-password-confirm')),
            reset_password_token.key)
    }

    # render email text
    email_html_message = render_to_string('password_reset_email.html', context)
    email_plaintext_message = render_to_string('password_reset_email.txt', context)

    msg = EmailMultiAlternatives(

        "Password Reset for {title}".format(title="CIVS & Baddies"),

        email_plaintext_message,

        "ezechukwe@devcenter.africa",

        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
    
    
    