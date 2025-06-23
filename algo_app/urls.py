from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path
from .views import (
    RequestPhoneOTP,
    UserSignup,
    UserLogin,
    UserLogout,
    ForgotPassword,
    RunStrategy,
    StopStrategy,
    PreviousOrderList,
    view_wallet,
    ConnectAccount,
    get_tokens_data,
    get_trade_details,
    index_expiry,
    index_strike_price,
    ListUserAPIView,
    UpdateUserStatusAPIView,
    UserInfo,
    RequestEmailOTP,
    VerifyEmailOTP,
    Register,
    VerifyPhoneOTP

)

urlpatterns = [
    #new onbording flow APIs
    path('request-email-otp/', RequestEmailOTP.as_view()),
    path('verify-email-otp/', VerifyEmailOTP.as_view()),
    path('register/', Register.as_view()),

    #verfy phone APIs
    path('user-info/', UserInfo.as_view()),
    path('request-phone-otp/', RequestPhoneOTP.as_view()),
    path('verify-phone-otp/',  VerifyPhoneOTP.as_view()),


    path('login/', UserLogin.as_view()),
    path('signup/', UserSignup.as_view()), 
    path('update-password/', ForgotPassword.as_view()),
    path('logout/', UserLogout.as_view()),
    path('start/', RunStrategy.as_view(), name="start"),
    path('stop/', StopStrategy.as_view(), name="stop"),
    path('order-history/', PreviousOrderList.as_view(), name="order_history"),
    path('view/', view_wallet, name='view_wallet'),
    path('connect-account/', ConnectAccount.as_view(), name='connect_account'),
    path('tokens/', get_tokens_data.as_view(), name='tokens'),
    path('trade-details/', get_trade_details.as_view(), name='trade_details'),
    path('token/<str:index>/', index_expiry.as_view(), name='index_expiry'),
    path('token/<str:index>/<str:expiry>/', index_strike_price.as_view(), name='index_strike_price'),
    path('trade-details/', get_trade_details.as_view(), name='get_trade_details'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/', ListUserAPIView.as_view(), name='list-users'),
    path("users/update-status/<str:id>/", UpdateUserStatusAPIView.as_view(), name="update-user-status"),

]

