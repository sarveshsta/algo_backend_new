from django.urls import path
from .views import (
    RequestOTP,
    VerifyOTP,
    UserSignup,
    UserLogin,
    UserLogout,
    ForgotPassword,
    RunStrategy,
    StopStrategy,
    PreviousOrderList,
    view_wallet,
)

urlpatterns = [
    path('request-otp/', RequestOTP.as_view()),
    path('verify-otp/', VerifyOTP.as_view()),
    path('signup/', UserSignup.as_view()),
    path('login/', UserLogin.as_view()),
    path('update-password/', ForgotPassword.as_view()),
    path('logout/', UserLogout.as_view()),
    path('start/', RunStrategy.as_view(), name="start"),
    path('stop/', StopStrategy.as_view(), name="stop"),
    path('order-history/', PreviousOrderList.as_view(), name="order_history"),
    path('view/', view_wallet, name='view_wallet')

]