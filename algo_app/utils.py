from cryptography.fernet import Fernet
import json
from twilio.rest import Client
from algo_today.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken,RefreshToken
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.conf import settings
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import serializers

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

#SEND VERIFICATION

def send_otp(otp, to_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.messages.create(
            body = f'Greetings, your OTP for Algo-Today is {otp}. Please do not share it with anyone.',
            from_= '+12034634291',
            to = '+918839003067'
        )


def set_user_custom_claims(user,access_token):
    access_token['email'] = user.email
    access_token['id'] = str(user.id)
    return access_token


def create_token_for_user(user):
    token = AccessToken.for_user(user)
    refesh_token = RefreshToken.for_user(user)
    access_token = refesh_token.access_token
    access_token = set_user_custom_claims(user,access_token)
    return {
        'access': str(access_token),
        'refresh': str(refesh_token)
    }

#CUSTOM EXCEPTION HANDLER
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        response = Response({
            'success': False,
            "mesage":"User is Unauthorized",
            'error': 'Authentication failed. Your token is invalid or expired.'
        }, status=status.HTTP_401_UNAUTHORIZED)
    if isinstance(exc, ValidationError):
            response.data = {
                'success': False,
                'message': 'Validation failed',
                'errors': response.data
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
    return response



#API RESPONSE
def response(success=False, data=None, message=None, error=None):
    response = {
        'success': success,
        'data': data if data is not None else {},
        'message': message if message is not None else 'something went wrong',
        'error': error if error is not None else 'null'
    }
    return response




fernet = Fernet(settings.FERNET_KEY.encode())

def generate_encrypted_token(user_id: str, email: str):
    payload = {"user_id": str(user_id), "email": email}
    try:
        encrypted_token = fernet.encrypt(json.dumps(payload).encode()).decode()
        return encrypted_token
    except Exception as e:
        raise Exception(f"Token encryption failed: {str(e)}")



def decrypt_encrypted_token(encrypted_token: str):
    try:
        decrypted_payload = fernet.decrypt(encrypted_token.encode()).decode()
        data = json.loads(decrypted_payload)
        return data 
    
    except Exception as e:
        raise ValueError(f"Invalid token or decryption failed: {str(e)}")


# pagination.py or utils.py
class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            "data": data,
            "meta": {
                "total_items": self.page.paginator.count,
                "total_pages": self.page.paginator.num_pages,
                "current_page": self.page.number,
                "page_size": self.get_page_size(self.request)
            }
        })



def send_email(subject, recipients, template_name, context):
    try:
        html_body = render_to_string(template_name, context)
        from_email = f"AlgoToday <{settings.DEFAULT_FROM_EMAIL}>"
        msg = EmailMultiAlternatives(subject, '', from_email, recipients)
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
