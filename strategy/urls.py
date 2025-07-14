from django.urls import path
from .views import (
   StartStrategyAPIView, 
   CreateStrategyWithConditionsAPIView,
   ListActiveStrategiesByAdminAPIView
)

urlpatterns = [
    path("create-strategy-with-conditions/", CreateStrategyWithConditionsAPIView.as_view(), name = 'create_strategy_with_conditions'),
    path("start-strategy/", StartStrategyAPIView.as_view(), name="start_strategy"),
    path("all-strategy/", ListActiveStrategiesByAdminAPIView.as_view(), name="all_strategy"),
]
