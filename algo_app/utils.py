from cryptography.fernet import Fernet
import json
from twilio.rest import Client
from algo_today.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated , PermissionDenied 
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
from .models import PhoneOTP,User
from subscriptions.models import UserSubscription
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import requests
import time
import random

#SEND VERIFICATION

def send_otp(otp, to_number):
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    client.messages.create(
        body=f'Greetings, your OTP for Algo-Today is {otp}. Please do not share it with anyone.',
        from_='+12295151945',
        to=f'+91{to_number}'
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
             'data': {},
            "message":"User is Unauthorized",
            'error': 'Authentication failed. Your token is invalid or expired.'
        }, status=status.HTTP_401_UNAUTHORIZED)

    elif isinstance(exc, PermissionDenied):
        return Response({
            'success': False,
            'data': {},
            'message': str(exc),
            'error': 'Permission denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    if isinstance(exc, ValidationError):
            response.data = {
                'success': False,
                'data': {},
                'message': 'Validation failed',
                'errors': response.data
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
    return response


# your_app/serializers.py
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            return {
                'success': True,
                'data': {
                    'refresh': data['refresh'],
                    'access': data['access']
                },
                'message': 'Login successful',
                'error': None
            }
        except AuthenticationFailed as e:
            # This handles invalid credentials
            return {
                'success': False,
                'data': {},
                'message': 'Invalid credentials',
                'error': str(e)
            }



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


INDICES = [
    "NIFTY 50",
    "NIFTY BANK",
    "NIFTY FIN SERVICE",
    "NIFTY MIDCAP SELECT"
]

def get_index_data(index_name, session, headers):
    # Step 3: Construct API URL
    url = f"https://www.nseindia.com/api/equity-stockIndices?index={index_name.replace(' ', '%20')}"
    try:
        response = session.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                entry = data['data'][0]
                return {
                    "index": entry.get('indexName', index_name),
                    "price": entry.get('lastPrice'),
                    "change": entry.get('change'),
                    "pChange": entry.get('pChange'),
                    "timestamp": entry.get('timeVal')
                }
            else:
                return {"error": f"No data found for {index_name}"}
        else:
            return {"error": f"Failed to fetch {index_name}, Status: {response.status_code}"}
    except Exception as e:
        return {"error": f"Error fetching {index_name}: {e}"}

def fetch_all_indices():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
        # 'cookie': 'AKA_A2=A; nsit=byTvvwO991W1iTEckeAWOcgx; nseappid=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhcGkubnNlIiwiYXVkIjoiYXBpLm5zZSIsImlhdCI6MTc1Mzc5MDkwNCwiZXhwIjoxNzUzNzk4MTA0fQ.9zMqrJGoo7qEP8xOK--5cFxhfoIc0wiK3Bwl4lvU9Og; bm_mi=DFAE431622477E0A52A1E8351F0A9454~YAAQV7csMc3RWTWYAQAA3Y4WVhz3e+eqXF8uHyVkBkmhkX8KSIFEXkD91bo2QSIPkXCYHglKLy0YwahvFd52OzCUjgAGwxTLTs7E+e/xfqr2GOvoOFj50sYm9mIigpslibF0B3e0g2fLjTyOpCX5y/8QXeJAQsoY37UIWmMkZO9/LY/r2gsNXA/t+F7CLRGjNsM6k/1rjJui71YN9ZdJFVPtXVO+4kVbvYdnlp1WP/CKuwHUyoWqjMhZaUV58JywTcQV0jZ1/j8bX576wsNJxisLwZp/KlDuMjxvaShTH3oS65er1OhrXieGgp0y0LygpLZegPVxXNyksmgkfi1QnJAgw9a5RoFD~1; bm_sz=A0DFB333EBF8696EDB3E864599A94391~YAAQV7csMc/RWTWYAQAA3Y4WVhxhoJhSgDS2zdQUq6LaiLqCC+1uWLzFc5EcHW9/ezmNBlTd6RCqSin++98Ht4SJv1LTyt3TURqUGvDrlz6PUcU1mQycCb3OKiu/3PYSBtK1AOyHWsgrvghVsPgWyxnb4VQJeKRYYAXJIbEkrwJS/s40YEc+D0fZc4/AKKgh934DYQVfl07AjN8+ogx1bMUynJloV+24A+vLuuuQU+mJxK+wAcZcgH4IjAQcSPvR4P/Ig0uLv2MRqeuReRaIZxVdpOnCIPNVfUz7EebloNwn6izja75iICqRhW3RALjX/3htWCjVmQYDiliDa6BWw1tadWG6LVce1gJ42PBkWYBnhHUXaN5vdPcnqR0B5i8fKTA+NKhEAyOD06VuWcg0h4m67b2r0Y4XcDwRVVfG8Aj8nmVbisgDnwxapj02VDVJFck=~3162672~4338231; _abck=27B3BFA6E19AF99B062508067D9CDC6E~0~YAAQV7csMdDRWTWYAQAAKY8WVg4P/Jzl/wGW8ibj936Wx3OE8I0pSB5LYtuuHo5FUV0g8oPYouz+OglolhtbpF52sn9Nnf+SK1HyZ9tqD6SvMp/61a9ai5LpSV1pTbKaPfDZtQPbEYib1sKLHUqW8IZor3EDgQjb9+EMmLFaNS0bJiYiErPRzXPfFOMoJjYYu+BFNT9AEG2lEJnmzrjk5Jmg4GUruK9VQsXVYNEIE2ZwsziSeHGusT24FLSI8Bz8yT4CkpHuV4egkowlByaDgUkGEBgO+wts+KcygO0lfrTwPdw/r3yEeCrz3LaZ4l5HW8xrkvjZ8MUe3c1IBZloZMrAhOdATMPM53NS7xt81J8G3+6FY7A03L+6pHO3YK5h6MRN6JGf9baddczfL5NMpwiGA4N/8L6m2flOlGsbdemEW4eGR/c0MGgCkPQ2LHznYFyKNDFLAbe2UB1V68z98SmoUcO5qIZXePJldn/XsH2C8GfbXHBB2tEIn9qrGTMnYH3zqb7EkFLUnxCPqKdDjwNlzcXvPFZMVWF18mYU/WO14L4MFLt1TOSPLlB4JXA1bWkOuVNLkTMgS285wn5ACtNTKZ+nEC1bLu2CqGE+n4JJiYEmF0U9UgDrNkzGXKg=~-1~-1~-1; bm_sv=EDAE022D0A63C464B0023F279DCF33BC~YAAQV7csMXbTWTWYAQAA7scWVhzUzKiQgAp56es8kBOXX6ScAIvTN/2mxP8DTIFyd6Qb8zpauVvkwI99gUau6ma0fZokmKU01sWHHQXtJySEEhslOB/c4ZwO58YaMmaMuPhy2JswzIGnq4+KzcZN/9vREQCnhKzlVtI86ASqLiFsD1mP1E6BVe8mdP1/0VwNMsRkRpndlJJQwbzYHao3ZI7rTjbCl1EjViiQ4lZHwW0FKuMzogVFd/F3fQfPkw81f7dP~1; ak_bmsc=542A0C38A09FAC3EB6427AC83275A9DA~000000000000000000000000000000~YAAQV7csMVgEWjWYAQAAgQwbVhzlfKu/t6gGMk5TJovRCoemhVw21S0s0khguo3gH5gTnf6trofioJO6a+LkkWE9ZSFcj6wLuVV2P7VsmMIUdkoHBgumuhsSXICqffHMdwgn4mNRe0dD4PZzmNLRZQQSO6wu+zv0KvAXCveuNAWEcQj84RQwoDHKhPLTwoREnpIj5QkawuuGJ6Q0iaENYg6qfLGtXzGnQYkNetSoN2dP2ywlHHwQUnTJXVWPmlKoF6h0LplR/BDobL1ZeEbbss2cRfakSILJU0Q3EdWyGNoB2UVLsOFDfBJeT/FUqyw23gLIuSKxpqtOGajazqpbvPHt+5WQoY4mWXb8ey2hJmnmjzq2bjDBbn7xdvJ1C1KocdnxM9S4O7vyyCfaflDl6JEf4wwqd2sgF384MBxtvl42DSreMUpKav17nLYq+T253m4iDLo=',
    }

    session = requests.Session()

    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
  

        # Step 2: Visit market data page
        session.get("https://www.nseindia.com/market-data/live-equity-market", headers=headers, timeout=10)
 

        # Step 3: Fetch all index data
        all_data = {}
        for index in INDICES:
            data = get_index_data(index, session, headers)
            all_data[index] = data
          

        return all_data

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

