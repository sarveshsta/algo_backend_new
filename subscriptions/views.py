import hmac
import hashlib
from django.conf import settings
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .serializers import (
    SubscriptionPlanSerializer,
    UserSubscriptionSerializer,
    PaymentSerializer,
)
from .razorpay_helper import (
    create_razorpay_plan,
    create_razorpay_subscription,
    create_razorpay_order,
    verify_signature,
)
from rest_framework import generics, filters, status
from algo_app.utils import CustomPagination, response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import SubscriptionPlan, UserSubscription, Payment, SubscriptionHistory


class SubscriptionPlanCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = SubscriptionPlanSerializer(data=request.data)
        if serializer.is_valid():
            plan = serializer.save()
            razorpay_plan = create_razorpay_plan(plan)
            plan.razorpay_plan_id = razorpay_plan.get("id")
            plan.save()
            return Response(SubscriptionPlanSerializer(plan).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionPlanListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        serializer = SubscriptionPlanSerializer(plans, many=True)
        return Response(serializer.data)


class CreateSubscriptionView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        plan_id = request.data.get("plan_id")

        try:
            plan = SubscriptionPlan.objects.get(id=plan_id, is_active=True)
        except SubscriptionPlan.DoesNotExist:
            return Response({"error": "Invalid plan selected"}, status=400)

        # Create Razorpay subscription and order
        razorpay_subscription = create_razorpay_subscription(plan.razorpay_plan_id, user.email)
        razorpay_order = create_razorpay_order(plan.price)

        # Create user subscription and payment record
        user_subscription = UserSubscription.objects.create(
            user=user,
            plan=plan,
            razorpay_subscription_id=razorpay_subscription["id"],
            status="pending",
            auto_renew=False
        )

        Payment.objects.create(
            user=user,
            subscription=user_subscription,
            razorpay_order_id=razorpay_order["id"],
            amount=plan.price
        )

        return Response({
            "subscription_id": str(user_subscription.id),
            "razorpay_subscription_id": razorpay_subscription["id"],
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key": settings.RAZORPAY_KEY_ID,
            "amount": float(plan.price),
            "currency": "INR"
        }, status=201)


class VerifyPaymentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        data = request.data
        order_id = data.get("razorpay_order_id")
        payment_id = data.get("razorpay_payment_id")
        signature = data.get("razorpay_signature")

        try:
            payment = Payment.objects.get(razorpay_order_id=order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=404)

        if not verify_signature({
            "razorpay_order_id": order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        }):
            payment.status = "failed"
            payment.save()
            return Response({"error": "Invalid payment signature"}, status=400)

        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.status = "completed"
        payment.save()

        sub = payment.subscription
        sub.status = "active"
        sub.start_date = timezone.now()
        sub.end_date = sub.start_date + timezone.timedelta(
            days=sub.plan.duration_value * (30 if sub.plan.duration_type == "monthly" else 365 if sub.plan.duration_type == "yearly" else 7)
        )
        sub.save()

        SubscriptionHistory.objects.create(
            user=sub.user,
            plan=sub.plan,
            action="activated",
            details={"source": "verify-payment", "payment_id": payment_id}
        )

        return Response({"message": "Payment verified, subscription activated"}, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookView(APIView):
    def post(self, request):
        webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
        received_signature = request.headers.get("X-Razorpay-Signature")
        body = request.body.decode()

        generated_signature = hmac.new(
            webhook_secret.encode(),
            body.encode(),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, generated_signature):
            return Response({"error": "Invalid signature"}, status=400)

        payload = request.data
        event = payload.get("event", "")
        payload_data = payload.get("payload", {})

        try:
            if event == "payment.captured":
                payment_id = payload_data["payment"]["entity"]["id"]
                order_id = payload_data["payment"]["entity"]["order_id"]
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()

                if payment and payment.status != "completed":
                    payment.razorpay_payment_id = payment_id
                    payment.status = "completed"
                    payment.save()

                    sub = payment.subscription
                    sub.status = "active"
                    sub.start_date = timezone.now()
                    sub.end_date = sub.start_date + timezone.timedelta(
                        days=sub.plan.duration_value * (30 if sub.plan.duration_type == "monthly" else 365 if sub.plan.duration_type == "yearly" else 7)
                    )
                    sub.save()

                    SubscriptionHistory.objects.create(
                        user=sub.user,
                        plan=sub.plan,
                        action="activated",
                        details={"source": "webhook", "payment_id": payment_id}
                    )

            elif event == "subscription.completed":
                sub_id = payload_data["subscription"]["entity"]["id"]
                sub = UserSubscription.objects.filter(razorpay_subscription_id=sub_id).first()
                if sub:
                    sub.status = "expired"
                    sub.save()

                    SubscriptionHistory.objects.create(
                        user=sub.user,
                        plan=sub.plan,
                        action="expired",
                        details={"source": "webhook"}
                    )

            elif event == "payment.failed":
                order_id = payload_data["payment"]["entity"]["order_id"]
                payment = Payment.objects.filter(razorpay_order_id=order_id).first()
                if payment:
                    payment.status = "failed"
                    payment.failure_reason = payload_data["payment"]["entity"].get("error_description", "Unknown")
                    payment.save()

                    SubscriptionHistory.objects.create(
                        user=payment.user,
                        plan=payment.subscription.plan,
                        action="failed",
                        details={"source": "webhook"}
                    )

        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({"status": "Webhook handled"}, status=200)




class ListUserSubscriptionAPIView(generics.ListAPIView):
    queryset = UserSubscription.objects.all().order_by('created_at')
    serializer_class = UserSubscriptionSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAdminUser]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ['status']

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