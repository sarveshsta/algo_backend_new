import random
from django.db.models import Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import login, logout
from django.contrib.auth.hashers import check_password
from .serializers import (
    LoginSerializer,
    SignupSerializer,
    UserSerializer,
    UpdateUserStatusSerializer,
    StrategySerializer
)
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework import generics, filters, status
from .models import PhoneOTP, User, Wallet, Transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .utils import send_otp, create_token_for_user, response,CustomPagination
from .utility import start_strategy, stop_strategy, connect_account, get_tokens, trade_details, get_index_expiry, get_index_strike_price


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
                # send_otp(otp, phone)
                return Response(response(True, {"otp": 123456}, "OTP sent"), status=status.HTTP_200_OK)

            # send_otp(otp, phone)
            
            phoneOTP_obj, create_status = PhoneOTP.objects.get_or_create(phone=phone)
            phoneOTP_obj.otp = otp
            print("OTP", otp)
            phoneOTP_obj.save()
            
            return Response(response(True, {"otp": otp}, "OTP sent"), status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)


class VerifyOTP(APIView):
    def post(self, request):
        data = self.request.data
        phone = data['phone']
        otp = data['otp']

        try:
            phoneotp_obj = PhoneOTP.objects.get(phone=phone, otp=otp)
            phoneotp_obj.is_verified = True
            phoneotp_obj.save()
            return Response(response(True, message ="OTP Verified"), status=status.HTTP_200_OK)
        except PhoneOTP.DoesNotExist:
            return Response(response(message ="Invalid OTP"), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)


class UserLogin(APIView):
    serialzer_class = LoginSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serialzer_class(data=data)

        if not serializer.is_valid():
            return Response(response(message = str(serializer.errors)), status=status.HTTP_400_BAD_REQUEST)
        
        phone = data['phone']
        otp = data['otp']
        password = data['password']

        try:
            PhoneOTP.objects.get(phone=phone, otp=otp, is_verified=True)
            user = User.objects.get(phone=phone)
            print(user)
            if check_password(password, user.password):
                login(request, user)
                tokens = create_token_for_user(user)
                print(tokens, "tokes")
                return Response(response(True, tokens,"Login successful"), status=status.HTTP_200_OK)
            else:
                return Response(response(message="Invalid credentials" ), status=status.HTTP_401_UNAUTHORIZED)
        except PhoneOTP.DoesNotExist:
            return Response(response(message="Invalid OTP" ), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)
        

class UserSignup(APIView):
    serializer_class = SignupSerializer
    def post(self, request):
        data = self.request.data
        serializer = self.serializer_class(data=data)

        if not serializer.is_valid():
            print(serializer.errors)
            return Response(response(message=str(serializer.errors) ), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            phone = data.get('phone')
            otp = data.get('otp')
            email = data.get('email')
            name = data.get('name')
            password = data.get('password')


            PhoneOTP.objects.get(phone=phone, otp=otp, is_verified=True)

            if User.objects.filter(Q(phone=phone)|Q(email=email)).exists():
                return Response(response(message="Email/Phone already exists"), status=status.HTTP_400_BAD_REQUEST)
            
            user = User.objects.create(email=email, phone=phone, name=name)
            user.set_password(password)
            user.save()
            tokens = create_token_for_user(user)
            print(tokens, "tokens")
            return Response(response(True, tokens,message="Signup successful"), status=status.HTTP_201_CREATED)
        except PhoneOTP.DoesNotExist:
            print("Error---->", str(e))
            return Response(response(True,message="Invalid OTP" ), status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(message="somthing went wrong", error=str(e)), status=status.HTTP_400_BAD_REQUEST)
        

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
            print("Error---->", str(e))
            return Response({"message": "User Does not exist", "success":False}, status=status.HTTP_400_BAD_REQUEST)
        except PhoneOTP.DoesNotExist:
            print("Error---->", str(e))
            return Response({"message": "Invalid OTP", "success":False}, status=status.HTTP_400_BAD_REQUEST)
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
    permission_classes = [IsAuthenticated]
    def post(self, request):
        try:
            user_id = request.user.id
            response = connect_account(request.data, user_id)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response(response(True, data, "Data retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)),status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class index_strike_price(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, index, expiry, *args, **kwargs):
        try:
            data = get_index_strike_price(index, expiry)
            return Response(response(True, data, "Data retrieved successfully"), status=status.HTTP_200_OK)
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
        

