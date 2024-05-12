# users/managers.py

from django.apps import apps
from django.db import models
import datetime
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _lazy

from users.settings import REQUEST_CONTEXT_EXTRACTOR

def parse_remote_addr(request: HttpRequest) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.headers.get("X-Forwarded-For", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR", "")


def parse_ua_string(request: HttpRequest) -> str:
    """Extract client user-agent from request."""
    return request.headers.get("User-Agent", "")


class UserVisitManager(models.Manager):
    """Custom model manager for UserVisit objects."""
    
    def build(self, request: HttpRequest, timestamp: datetime.datetime):
        UservisitModel = apps.get_model('users', 'UserVisit')  # Lazy loading here
        uv = UservisitModel(
            user=request.user,
            timestamp=timestamp,
            session_key=request.session.session_key,
            remote_addr=parse_remote_addr(request),
            ua_string=parse_ua_string(request),
            context=REQUEST_CONTEXT_EXTRACTOR(request),
        )
        uv.hash = uv.md5().hexdigest()
        uv.browser = uv.user_agent.get_browser()[:200]
        uv.device = uv.user_agent.get_device()[:200]
        uv.os = uv.user_agent.get_os()[:200]
        return uv


from django.db import models


class AddressManager(models.Manager):

    def get_addresses_by_type(self, user_id, address_type):
        """
        Filters addresses for a specific user by address type (billing or shipping).

        Args:
            user_id (int): The ID of the user.
            address_type (str): The address type (Address.BILLING or Address.SHIPPING).

        Returns:
            QuerySet: A queryset containing the filtered addresses.
        """

        return self.get_queryset().filter(user_id=user_id, address_type=address_type)

    def get_default_address_by_type(self, user_id, address_type):
        """
        Retrieves the default address for a specific user and address type (billing or shipping).

        Args:
            user_id (int): The ID of the user.
            address_type (str): The address type (Address.BILLING or Address.SHIPPING).

        Returns:
            Address: The default address for the user and type, or None if not found.
        """

        return self.get_queryset().filter(user_id=user_id, address_type=address_type, default=True).first()

