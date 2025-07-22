import requests
from rest_framework.views import APIView
from .serializers import (CreateStrategySerializer, 
                          StrategyConditionSerializer, 
                          StrategyExecutionInputSerializer,
                          StrategySerializer,
                          StrategyDropdownSerializer)
from rest_framework.response import Response
from algo_app.utils import (response)
from rest_framework import status, serializers, generics, filters
    
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Strategy
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from algo_app.utils import CustomPagination, generate_encrypted_token
from algo_app.middlewares import IsVerified, HasActiveSubscription, HasConnectedAngelOneAccount
from algo_app.utility import stop_strategy, strategy_status





class CreateStrategyWithConditionsAPIView(APIView):
    permission_classes = [IsAdminUser]
    serializer_class = StrategyConditionSerializer

    def post(self, request):
        name = request.data.get("name")
        description = request.data.get("description")
        conditions_data = request.data.get("conditions", [])

        if not name or not description:
            return Response(response(False, message="`name` and `description` are required."),
                            status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(conditions_data, list) or not conditions_data:
            return Response(response(False, message="`conditions` must be a non-empty list."),
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Step 1: Create strategy first
                strategy = Strategy.objects.create(name=name, description=description,  created_by=request.user)

                # Step 2: Validate all conditions (now with strategy attached)
                condition_serializers = []
                for index, cond in enumerate(conditions_data):
                    cond["strategy"] = strategy.id  # ✅ Attach strategy before validation
                    serializer = self.serializer_class(data=cond)
                    if not serializer.is_valid():
                        # Rollback the strategy creation if any condition is invalid
                        raise serializers.ValidationError({index: serializer.errors})
                    condition_serializers.append(serializer)

                # Step 3: Save all validated conditions
                created_conditions = []
                for serializer in condition_serializers:
                    serializer.save()
                    created_conditions.append({
                        "id": str(serializer.instance.id),
                        "type": serializer.instance.type
                    })

                return Response(
                    response(True, {
                        "strategy_id": str(strategy.id),
                        "conditions": created_conditions
                    }, "Strategy and all conditions created successfully"),
                    status=status.HTTP_201_CREATED
                )

        except serializers.ValidationError as ve:
            return Response(
                response(False, message="Validation failed for condition", error=ve.detail),
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                response(False, message="Unexpected error occurred", error=str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


FASTAPI_URL = "http://localhost:8000/custome-strategy/run-strategy"  # move to .env ideally


class StartStrategyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerified, HasActiveSubscription, HasConnectedAngelOneAccount]
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        data = request.data
        serializer = StrategyExecutionInputSerializer(data=data)
        if not serializer.is_valid():
            return Response(response(False, message=serializer.errors), status=status.HTTP_400_BAD_REQUEST)

        try:
            strategy_id = data.get("strategy_id")
            strategy = Strategy.objects.prefetch_related("strategycondition_set").get(id=strategy_id)

            # Fetch all conditions with full strategy model fields
            conditions = strategy.strategycondition_set.all().values(
                "type",
                "comparison_type",
                "operator",
                "left_ohlc",
                "left_multiplier",
                "left_candle_offset",
                "right_ohlc",
                "right_multiplier",
                "right_candle_offset",
                "left_indicator",
                "left_factor",
                "left_candle_count",
                "right_indicator",
                "right_factor",
                "right_candle_count",
                "constant_value",
                "logic_operator",
                "value_type",
                "sl_tp_value",
            )

            payload = {
                **serializer.validated_data,
                "conditions": list(conditions)
            }

            # POST to FastAPI
            token = generate_encrypted_token(request.user.id, request.user.email)
            headers = {"Authorization": token}
            fastapi_response = requests.post(FASTAPI_URL, json=payload, headers=headers)

            if fastapi_response.status_code == 200:
                return Response(response(True, fastapi_response.json(), "Strategy execution started"), status=200)
            else:
                return Response(response(False, message="FastAPI error", error=fastapi_response.text), status=500)

        except Strategy.DoesNotExist:
            return Response(response(False, message="Strategy not found"), status=404)

        except Exception as e:
            print("Error →", str(e))
            return Response(response(False, message="Something went wrong", error=str(e)), status=500)

class StopStrategyAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerified, HasActiveSubscription, HasConnectedAngelOneAccount]
    # permission_classes = [IsAuthenticated]
    def post(self, *args, **kwargs):
        if not self.kwargs['strategy_id']:
            return Response("strategy_id is required", status_code=status.HTTP_400_BAD_REQUEST)
        response = stop_strategy(self.kwargs['strategy_id'])
        return Response(response, status=status.HTTP_200_OK)

class StrategyStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsVerified, HasActiveSubscription, HasConnectedAngelOneAccount]
    # permission_classes = [IsAuthenticated]

    def post(self, *args, **kwargs):
        if not self.kwargs['strategy_id']:
            return Response("strategy_id is required", status_code=status.HTTP_400_BAD_REQUEST)
        response = strategy_status(self.kwargs['strategy_id'])
        return Response(response, status=status.HTTP_200_OK)
class ListActiveStrategiesByAdminAPIView(generics.ListAPIView):
    queryset = Strategy.objects.filter(is_active=True, created_by__is_staff=True).order_by('-created_at')
    serializer_class = StrategySerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ["name", "is_active"]
    search_fields = ["name", "description"]

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(response(True, serializer.data, "Strategies retrieved successfully"))
            serializer = self.get_serializer(queryset, many=True)
            return Response(response(True, serializer.data, "Strategies retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ListStrategiesForDropdownAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            strategies = Strategy.objects.filter(is_active=True, created_by__is_staff=True).order_by('-created_at')
            serializer = StrategyDropdownSerializer(strategies, many=True)
            return Response(response(True, serializer.data, "Strategies retrieved successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            print("Error---->", str(e))
            return Response(response(error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
