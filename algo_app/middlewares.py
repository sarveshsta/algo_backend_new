# permissions.py
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import PhoneOTP, AngelOneCredential
from subscriptions.models import UserSubscription

class IsVerified(BasePermission):
    """
    Allows access only to users who have verified email and mobile.
    """
    def has_permission(self, request, view):
        user = request.user
        try:
            if not user.is_email_verified:
                raise PermissionDenied("Email is not verified")

            mobile_verify = PhoneOTP.objects.get(phone=user)
            if not mobile_verify.is_verified:
                raise PermissionDenied("Mobile number is not verified")
        except PhoneOTP.DoesNotExist:
            raise PermissionDenied("Mobile number record not found")
        return True

class HasActiveSubscription(BasePermission):
    """
    Allows access only to users with an active subscription.
    """
    def has_permission(self, request, view):
        user = request.user
        if not UserSubscription.objects.filter(user=user, status="active").exists():
            raise PermissionDenied("You do not have an active subscription")
        return True 
    
class HasConnectedAngelOneAccount(BasePermission):
    """
    Allows access only if the user has connected their AngelOne account.
    """
    def has_permission(self, request, view):
        user = request.user
        if not AngelOneCredential.objects.filter(user=user).exists():
            raise PermissionDenied("User has not connected their AngelOne account")
        return True

   