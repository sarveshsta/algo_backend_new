from rest_framework import serializers



class StrategySerializer(serializers.Serializer):
    strategy_id = serializers.CharField()
    index = serializers.CharField()
    strike_price = serializers.IntegerField()
    expiry = serializers.CharField()
    option = serializers.CharField()
    chart_time = serializers.CharField()
    
class LoginSerializer(serializers.Serializer):
    phone = serializers.IntegerField()
    otp = serializers.IntegerField()
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