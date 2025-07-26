import email
import random
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    SignupSerializer,
    UserSerializer,
    UpdateUserStatusSerializer,
    StrategySerializer,
    UserInfoSerializer
)
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import generics, filters, status
from .models import PhoneOTP, User, Wallet, Transaction, AngelOneCredential
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .utils import send_email, send_otp, create_token_for_user, response,CustomPagination
from .utility import start_strategy, stop_strategy, connect_account, get_tokens, trade_details, get_index_expiry, get_index_strike_price
from .middlewares import HasActiveSubscription, IsVerified, HasConnectedAngelOneAccount
# your_app/views.py
from rest_framework_simplejwt.views import TokenObtainPairView
from .utils import CustomTokenObtainPairSerializer
class RequestEmailOTP(APIView):
    def post(self, request):
        data = self.request.data
        email = data['email']
        try:
            otp = random.randint(100000, 999999)
            send_email(
                subject='Welcome to AlgoToday',
                recipients=[email],
                template_name='verification_email.html',
                context={'verification_code': otp}
            )
            
            user, create_status = User.objects.get_or_create(email=email)
            user.verification_code = otp
            print("OTP", otp)
            user.save()
            return Response(response(True, message="OTP sent"), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)
        
class VerifyEmailOTP(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        verification_code = data.get('otp')

        try:
            user = User.objects.get(email=email, verification_code=verification_code)
            user.is_email_verified = True
            user.save()
            return Response(response(True, message="OTP Verified"), status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response(response(message="Invalid OTP"), status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            print("Error:", str(e))
            return Response(response(message="Something went wrong", error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class Register(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(response(message=str(serializer.errors)), status=status.HTTP_400_BAD_REQUEST)

        try:
            email = data.get('email')
            phone = data.get('phone')
            name = data.get('name')
            password = data.get('password')

            user = User.objects.filter(email=email).first()
            if not user:
                return Response(response(message="Email does not exist or is not pre-registered"), status=status.HTTP_400_BAD_REQUEST)

            if not user.is_email_verified:
                return Response(response(message="Email is not verified"), status=status.HTTP_400_BAD_REQUEST)
            if user.phone and user.name and user.has_usable_password():
                return Response(
                    response(message="An account with this email is already registered."),
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.phone = phone
            user.set_password(password)
            user.name = name
            user.save()
            PhoneOTP.objects.create(phone=phone)
            tokens = create_token_for_user(user)
            user_data = UserInfoSerializer(user).data
            flat_data = { **user_data,**tokens}
            return Response(response(True, flat_data, message="Signup successful"), status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Error ---->", str(e))
            return Response(response(message="Something went wrong", error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            print(request.user)
            user = User.objects.get(id=request.user.id)
            if not user:
                return Response(response(error="user not found"), status=status.HTTP_400_BAD_REQUEST)
            phone = PhoneOTP.objects.get(phone = user.phone)
            if not phone:
                return Response(response(error="phone number not found"), status=status.HTTP_400_BAD_REQUEST)
            email_verified = user.is_email_verified if user else False
            phone_verified = phone.is_verified if phone else False

            # Serialize user
            serializer = UserInfoSerializer(user)
            user_data = serializer.data
            user_data['phone_verified'] = phone_verified  
            user_data['email_verified'] = email_verified 
            return Response(response(True, user_data, message="User info retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error ---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)
           
class RequestPhoneOTP(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        phone = data.get('phone')

        if not phone:
            return Response(response(message="Phone number is required"), status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=request.user.id)
            user.phone = phone
            user.save()
            PhoneOTP.objects.filter(phone=phone).delete()
            otp = random.randint(100000, 999999)
            PhoneOTP.objects.create(phone=phone, otp=otp)
            send_otp(otp, phone)
            return Response(response(True, {"otp": otp}, message="OTP sent successfully"), status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(response(False, message="User not found"), status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error ---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyPhoneOTP(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        phone = data.get('phone')
        otp = data.get('otp')

        if not phone or not otp:
            return Response(response(False, message="Phone and OTP are required"), status=status.HTTP_400_BAD_REQUEST)

        try:
            phone_otp = PhoneOTP.objects.filter(phone=phone, otp=otp).first()
            phone_otp.is_verified = True
            phone_otp.save()
            return Response(response(True, message="Phone verified successfully"), status=status.HTTP_200_OK)
        except PhoneOTP.DoesNotExist:
            return Response(response(False, message="Invalid otp"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Login(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            return Response(response(False, message=serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.filter(email=email, is_email_verified=True).first()
            if not user:
                return Response(response(False, message="User not found or email not verified"), status=status.HTTP_404_NOT_FOUND)
    
            if not user.is_active == True:
                return Response(response(False, message="admin has deactivate you account, contact support"), status=status.HTTP_400_BAD_REQUEST)

            if check_password(password, user.password):
                login(request, user)
                tokens = create_token_for_user(user)
                user_data = UserInfoSerializer(user).data
                flat_data = { **user_data,**tokens}
                return Response(response(True, flat_data, "Login successful"), status=status.HTTP_200_OK)
            else:
                return Response(response(False, message="Invalid credentials"), status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            print("Error ---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
       
class ForgotPassword(APIView):
    serializer_class = LoginSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            return Response({"message": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        
        email = data['email']
        password = data['password']

        try:
            user = User.objects.filter(email=email).first()
            user.set_password(password)  
            user.save()     
            return Response({"message": "Password Updated", "success": True}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User Does not exist", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error---->", str(e))
            return Response({"message": f"Error {e}", "success": False}, status=status.HTTP_400_BAD_REQUEST)


class UserLogout(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            print(request.user)
            logout(request)
            return Response(response(True,message="Logout success"), status=status.HTTP_200_OK )
        except Exception as e:
             print("Error---->", str(e))
             return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)


class ConnectAccount(APIView):
    permission_classes = [IsAuthenticated, IsVerified]

    def post(self, request):
        try:
            user_id = request.user.id
            if AngelOneCredential.objects.filter(user_id=user_id).exists():
                return Response(response(message="Account is already connected."),status=status.HTTP_400_BAD_REQUEST)

            # Proceed to connect the account
            res = connect_account(request.data, user_id)
            return Response(res, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error ---->", str(e))
            return Response(
                response(error=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class TradeAPI(APIView):
    def get(self, request):
        url = "https://google.com"
        r = requests.get(url)
        json_response = r.json()
        

class RunStrategy(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print(self.request.data)
        request.data["user_id"] = str(request.user.id) 
        request.data["strategy_id"] = "1"  

       
        print(self.request.data)
        response = start_strategy(request.data)
        return Response(response, status=status.HTTP_200_OK)


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


class get_tokens_data(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            data = get_tokens()
            return Response(response(True, data, "Data retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class get_trade_details(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            data = trade_details()
            return Response(response(True, data, "Data retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class index_expiry(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, *args, **kwargs):
        try:
            data = get_index_expiry(index)
            return Response(response(True, data.get('data'), "Data retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class index_strike_price(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, expiry, *args, **kwargs):
        try:
            data = get_index_strike_price(index, expiry)
            return Response(response(True, data.get('data'), "Data retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListUserAPIView(generics.ListAPIView):
    queryset = User.objects.all().order_by('created_at')
    serializer_class = UserSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ["name", "is_active"]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset) 
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(response(True, serializer.data, "Users retrieved successfully"))
            serializer = self.get_serializer(queryset, many=True)
            return Response(response(True, serializer.data, "Users retrieved successfully"),status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateUserStatusAPIView(generics.UpdateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UpdateUserStatusSerializer
  
    def get_object(self, id):
        if not id:
            raise Exception("id is required")
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            raise Exception("User not found")

    def update(self, request, id, *args, **kwargs):
        try:
            user = self.get_object(id)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.is_active = serializer.validated_data["is_active"]
            user.save()
            return Response(response(True, message="User status updated successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class CheckAngelOneConnectionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,*args, **kwargs):
        try:
            is_connected = AngelOneCredential.objects.filter(user=request.user.id).exists()

            if is_connected:
                return Response(response(True, message="AngelOne account is already connected"), status=status.HTTP_200_OK)
            else:
                return Response(response(False, message="AngelOne account is not connected"), status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(response(error="User not found"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(response(error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
