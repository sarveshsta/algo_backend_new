from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import StrategySerializer
from .utility import run_strategy, stop_strategy, previous_orders
import random
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PhoneOTP, User, Wallet, Transaction
from .serializers import (
    LoginSerializer,
    SignupSerializer,
)
from .utils import send_otp


class RequestOTP(APIView):
    def post(self, request):
        data = self.request.data
        phone = data['phone']
        try:
            otp = random.randint(100000, 999999)
            if str(phone) == "9630152559":
                phoneOTP_obj, create_status = PhoneOTP.objects.get_or_create(phone=phone)
                phoneOTP_obj.otp = 123456
                print("OTP", 123456)
                phoneOTP_obj.save()
                return Response({"message": "OTP sent", "success":True, "data":{"otp": 123456}}, status=status.HTTP_200_OK)

            #send_otp(otp, phone)
            
            phoneOTP_obj, create_status = PhoneOTP.objects.get_or_create(phone=phone)
            phoneOTP_obj.otp = otp
            print("OTP", otp)
            phoneOTP_obj.save()
            
            return Response({"message": "OTP sent", "success":True, "data":{"otp": otp}}, status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": f"Error - {e}", "success":False}, status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    def post(self, request):
        data = self.request.data
        phone = data['phone']
        otp = data['otp']

        try:
            phoneotp_obj = PhoneOTP.objects.get(phone=phone, otp=otp)
            phoneotp_obj.is_verified = True
            phoneotp_obj.save()
            return Response({"message": "OTP Verified", "success":True}, status=status.HTTP_200_OK)
        except PhoneOTP.DoesNotExist:
            return Response({"message": "Invalid OTP", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message":f"Error {e}", "success":False}, status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    serialzer_class = LoginSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serialzer_class(data=data)

        if not serializer.is_valid():
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
        phone = data['phone']
        otp = data['otp']
        password = data['password']

        try:
            PhoneOTP.objects.get(phone=phone, otp=otp, is_verified=True)
            user = User.objects.get(phone=phone)
            print(user)
            if check_password(password, user.password):
                login(request, user)
                return Response({"message": "Login successful", "success": True}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Invalid credentials", "success": False}, status=status.HTTP_401_UNAUTHORIZED)
        except PhoneOTP.DoesNotExist:
            return Response({"message": "Invalid OTP", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message": f"Error {e}", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        
    # def _generate_jwt_token(self, user):
    #     payload = {
    #         'user_id': str(user.id),
    #         'exp': datetime.utcnow() + timedelta(days=1),  # Token expiration time (1 day in this example)
    #         'iat': datetime.utcnow(),  # Issued at time
    #     }
    #     token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256').decode('utf-8')
    #     return token


class UserSignup(APIView):
    serialzer_class = SignupSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serialzer_class(data=data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            phone = data['phone']
            otp = data['otp']
            email = data['email']
            name = data['name']
            password = data['password']

            PhoneOTP.objects.get(phone=phone, otp=otp, is_verified=True)

            if User.objects.filter(Q(phone=phone)|Q(email=email)).exists():
                return Response({"message":"Email/Phone already exists", "success":False}, status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create(email=email, phone=phone, name=name)
            user.set_password(password)
            user.save()
            return Response({"message": "Signup successful", "success": True}, status=status.HTTP_201_CREATED)
        except PhoneOTP.DoesNotExist:
            return Response({"message": "Invalid OTP", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({"message": f"Error {e}", "success": False}, status=status.HTTP_400_BAD_REQUEST)
        

class ForgotPassword(APIView):
    serialzer_class = LoginSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serialzer_class(data=data)

        if not serializer.is_valid():
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
        phone = data['phone']
        otp = data['otp']
        password = data['password']

        try:
            PhoneOTP.objects.get(phone=phone, otp=otp, is_verified=True)
            user = User.objects.get(phone=phone)
            
            user.set_password(password)  
            user.save()     
            return Response({"message": "Password Updated", "success": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User Does not exist", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneOTP.DoesNotExist:
            return Response({"message": "Invalid OTP", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": f"Error {e}", "success": False}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    def post(self, request):
        try:
            print(request.user)
            logout(request)
            return Response({"message": "Logout success", "success":True}, status=status.HTTP_200_OK )
        except Exception as e:
            return Response({"message": f"Failed to logout - {str(e)}", "success":False}, status=status.HTTP_400_BAD_REQUEST)

import requests
class TradeAPI(APIView):
    def get(self, request):
        url = "https://google.com"
        r = requests.get(url)
        json_response = r.json()
        

class RunStrategy(APIView):
    def post(self, request, *args, **kwargs):
        print(self.request.data)
        serializer = StrategySerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
        response = run_strategy(request.data, str(self.request.user.id))
        return Response(response, status_code=status.HTTP_200_OK)

class StopStrategy(APIView):
    def get(self, *args, **kwargs):
        if not self.kwargs['strategy_id']:
            return Response("strategy_id is required", status_code=status.HTTP_400_BAD_REQUEST)
        response = stop_strategy(self.kwargs['strategy_id'])
        return Response(response, status_code=status.HTTP_200_OK)

class PreviousOrderList(APIView):
    def get(self, request, *args, **kwargs):
        response = previous_orders(str(self.request.user.id))
        if not response:
            return Response({"message": "No Previous order found", "success": True}, status_code=status.HTTP_200_OK)
        return Response({"message": response, "success": True}, status_code=status.HTTP_200_OK)
    
def view_wallet(request):
    user = request.user
    try:
        # Fetch the wallet and transactions for the logged-in user
        wallet = Wallet.objects.get(user=user)
        transactions = Transaction.objects.filter(user=user).order_by('-created_at')
    except Wallet.DoesNotExist:
        wallet = None  # Or handle this case appropriately
        transactions = []
    except Exception as e:
        # Log the exception or handle it as needed
        print(f"An error occurred: {e}")
        wallet = None
        transactions = []

    context = {
        'wallet': wallet,
        'transactions': transactions
    }
     
    return Response({"message": "Logout success", "success":True}, status=status.HTTP_200_OK)