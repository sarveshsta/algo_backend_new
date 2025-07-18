import uuid
from rest_framework import serializers
from .models import SubscriptionPlan, UserSubscription, Payment
from algo_app.models import User


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = '__all__'

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'email']

class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'price', 'duration_type', 'duration_value']
class UserSubscriptionSerializer(serializers.ModelSerializer):
    user_detail = UserBasicSerializer(source='user', read_only=True)
    plan_detail = SubscriptionPlanSerializer(source='plan', read_only=True)
    class Meta:
        model = UserSubscription
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'



class UpdateSubscriptionPlanStatusSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    is_active = serializers.BooleanField()


class SubscriptionsPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = "__all__"