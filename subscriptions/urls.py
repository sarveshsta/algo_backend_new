from django.urls import path
from .views import (CreateSubscriptionView,
                    ListUserSubscriptionAPIView,
                    UserSubscriptionCancelAPIView,
                      VerifyPaymentView,
SubscriptionPlanListView,
SubscriptionCreateAPIView,
RazorpayWebhookView

                      )

urlpatterns = [
    path("plans/create/", SubscriptionCreateAPIView.as_view()),
    path("plans/", SubscriptionPlanListView.as_view()),
    path("create/", CreateSubscriptionView.as_view()),
    path("verify/", VerifyPaymentView.as_view()),
    path("webhook/razorpay/", RazorpayWebhookView.as_view()),
    path('users-subscriptions/', ListUserSubscriptionAPIView.as_view(), name='list-users'),
    path('user-subscription-cancel/',UserSubscriptionCancelAPIView.as_view(),name='user-subscription-cancel')
]
