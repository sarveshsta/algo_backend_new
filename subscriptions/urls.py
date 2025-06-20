from django.urls import path
from .views import (
    SubscriptionPlanCreateView,
    SubscriptionPlanListView,
    CreateSubscriptionView,
    VerifyPaymentView,
    RazorpayWebhookView,
    ListUserSubscriptionAPIView
)

urlpatterns = [
    path("plans/create/", SubscriptionPlanCreateView.as_view()),
    path("plans/", SubscriptionPlanListView.as_view()),
    path("subscription/create/", CreateSubscriptionView.as_view()),
    path("subscription/verify/", VerifyPaymentView.as_view()),
    path("webhook/razorpay/", RazorpayWebhookView.as_view()),
    path('users-subscriptions/', ListUserSubscriptionAPIView.as_view(), name='list-users'),
]
