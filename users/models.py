from __future__ import annotations
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
import datetime
import hashlib
import uuid
from django_countries.fields import CountryField
from typing import Any
from django.core.cache import cache
import user_agents
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _lazy
from users.managers import AddressManager, UserVisitManager
from users.settings import REQUEST_CONTEXT_ENCODER
from rest_framework_simplejwt.tokens import RefreshToken
import uuid
from django.core.validators import RegexValidator



class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    customer_id = models.CharField(max_length=20, verbose_name=_lazy("Customer ID"), null=True, unique=True)
    full_name = models.CharField(max_length=100, verbose_name=_lazy("Full Name"), null=True, blank=False)
    email = models.EmailField(max_length=255, verbose_name=_lazy("Email Address"), unique=True)
    mobile = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r"^\d{10,15}$", message="Enter a valid mobile number")],
        verbose_name=_lazy("Mobile Number"),
        unique=True,
        null=True,
        blank=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)  
    activation_token = models.CharField(max_length=100, blank=True, null=True, editable=False) 
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        ordering = ("-created_at",)
        verbose_name = _lazy("User")
        verbose_name_plural = _lazy("Users")

    def __str__(self):
        return self.full_name or self.email
    
    def get_full_name(self):
        return self.full_name
    
    def tokens(self):    
        refresh = RefreshToken.for_user(self)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }

    def save(self, *args, **kwargs):
        if not self.customer_id:  # Only generate if not provided
            if self.is_staff:
                prefix = "ADMIN"
            else:
                prefix = "CUS"

            # Get the last four digits of the phone number
            last_four_digits = str(self.mobile)[-4:] if self.mobile else "0000"
            # Get the total number of users with the prefix
            total_users_with_prefix = CustomUser.objects.filter(customer_id__startswith=f"{prefix}-").count()
            # Increment by 1 and pad with zeros
            count_padded = str(total_users_with_prefix + 1).zfill(3)
            # Concatenate the parts to generate the customer_id
            self.customer_id = f"{prefix}-{count_padded}-{last_four_digits}"
        super().save(*args, **kwargs)
  


class Address(models.Model):

    BILLING = "B"
    SHIPPING = "S"

    ADDRESS_CHOICES = (
        (BILLING, _lazy("Billing")),
        (SHIPPING, _lazy("Shipping")),
    )

    user = models.ForeignKey(CustomUser, related_name="addresses", on_delete=models.CASCADE)
    address_type = models.CharField(max_length=1, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    country = CountryField()
    city = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AddressManager()

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.user.get_full_name()

    def is_billing_address(self):
        return self.address_type == self.BILLING

    def is_shipping_address(self):
        return self.address_type == self.SHIPPING
    

    
class AdminProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(CustomUser, related_name="profile", on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatar", blank=True, null=True)
    location = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.user.get_full_name()
    
    @property
    def last_seen(self):
        return cache.get(f"seen_{self.user.username}")

    @property
    def online(self):
        if self.last_seen:
            now = datetime.now(timezone.utc)
            if now > self.last_seen + datetime.timedelta(minutes=settings.USER_ONLINE_TIMEOUT):
                return False
            else:
                return True
        else:
            return False



class CustomerProfile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    avatar = models.ImageField(upload_to="customer_avatar", blank=True, null=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="customer_profile")
    address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name="address", null=True, blank=True)


    def __str__(self):
        return self.user.get_full_name()

  
    
class LoginLog(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    login_time = models.DateTimeField(default=timezone.now)
    login_failed = models.BooleanField(default=False)
    logout_time = models.BooleanField(default=False)
    login_location = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    

class UserVisit(models.Model):
    """
    Record of a user visiting the site on a given day.

    This is used for tracking and reporting - knowing the volume of visitors
    to the site, and being able to report on someone's interaction with the site.

    We record minimal info required to identify user sessions, plus changes in
    IP and device. This is useful in identifying suspicious activity (multiple
    logins from different locations).

    Also helpful in identifying support issues (as getting useful browser data
    out of users can be very difficult over live chat).
    """
    user = models.ForeignKey(CustomUser, related_name="user_visits", on_delete=models.CASCADE
    )
    timestamp = models.DateTimeField(
        help_text=_lazy("The time at which the first visit of the day was recorded"),
        default=timezone.now,
    )
    session_key = models.CharField(help_text="Django session identifier", max_length=40)
    remote_addr = models.CharField(
        help_text=_lazy(
            "Client IP address (from X-Forwarded-For HTTP header, "
            "or REMOTE_ADDR request property)"
        ),
        max_length=100,
        blank=True,
    )
    ua_string = models.TextField(
        _lazy("User agent (raw)"),
        help_text=_lazy("Client User-Agent HTTP header"),
        blank=True,
    )
    browser = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )
    device = models.CharField(
        _lazy("Device type"), 
        max_length=200,
        blank=True,
        default="",
    )
    os = models.CharField(
        _lazy("Operating System"),
        max_length=200,
        blank=True,
        default="",
    )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    hash = models.CharField(  # noqa: A003
        max_length=32,
        help_text=_lazy("MD5 hash generated from request properties"),
        unique=True,
    )
    created_at = models.DateTimeField(
        help_text=_lazy(
            "The time at which the database record was created (!=timestamp)"
        ),
        auto_now_add=True,
    )
    context = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        encoder=REQUEST_CONTEXT_ENCODER,
        help_text=_lazy("Used for storing ad hoc / ephemeral data - e.g. GeoIP."),
    )

    objects = UserVisitManager()

    class Meta:
        get_latest_by = "timestamp"

    def __str__(self) -> str:
        return f"{self.user} visited the site on {self.timestamp}"

    def __repr__(self) -> str:
        return f"<UserVisit id={self.id} user_id={self.user_id} date='{self.date}'>"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Set hash property and save object."""
        self.hash = self.md5().hexdigest()
        super().save(*args, **kwargs)

    @property
    def user_agent(self) -> user_agents.parsers.UserAgent:
        """Return UserAgent object from the raw user_agent string."""
        return user_agents.parsers.parse(self.ua_string)

    @property
    def date(self) -> datetime.date:
        """Extract the date of the visit from the timestamp."""
        return self.timestamp.date()

    # see https://github.com/python/typeshed/issues/2928 re. return type
    def md5(self) -> hashlib._Hash:
        """Generate MD5 hash used to identify duplicate visits."""
        h = hashlib.md5(str(self.user.id).encode())  # noqa: S303, S324
        h.update(self.date.isoformat().encode())
        h.update(self.session_key.encode())
        h.update(self.remote_addr.encode())
        h.update(self.ua_string.encode())
        return h
