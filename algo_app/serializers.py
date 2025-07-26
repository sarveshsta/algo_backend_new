from.models import User
from rest_framework import serializers

class StrategySerializer(serializers.Serializer):
    strategy_id = serializers.CharField()
    index = serializers.CharField()
    strike_price = serializers.IntegerField()
    expiry = serializers.CharField()
    option = serializers.CharField()
    chart_time = serializers.CharField()
    
class LoginSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(max_length=30)
    
class SignupSerializer(serializers.Serializer):
    phone = serializers.IntegerField()
    otp = serializers.IntegerField()
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=30)
     
class SignupSerializer(serializers.Serializer):
    password = serializers.CharField()
    phone = serializers.IntegerField()

class RegisterSerializer(serializers.Serializer):
    phone = serializers.IntegerField()
    name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(max_length=30)




class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id","name", "email", "phone", "is_active", "created_at", "updated_at", "last_login", "is_superuser"]


class UpdateUserStatusSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "phone", "name", "username", "email"]

