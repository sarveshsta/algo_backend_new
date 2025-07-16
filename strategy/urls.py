from django.urls import path
from .views import (
   StartStrategyAPIView, 
   CreateStrategyWithConditionsAPIView,
   ListActiveStrategiesByAdminAPIView,
   StopStrategyAPIView,
   StrategyStatusAPIView,
   ListStrategiesForDropdownAPIView

)

urlpatterns = [
    path("create-strategy-with-conditions/", CreateStrategyWithConditionsAPIView.as_view(), name = 'create_strategy_with_conditions'),
    path("start-strategy/", StartStrategyAPIView.as_view(), name="start_strategy"),
    path("stop-strategy/<str:strategy_id>", StopStrategyAPIView.as_view(), name="stop_strategy"),
    path("strategy-status/<str:strategy_id>", StrategyStatusAPIView.as_view(), name="strategy_status"),
    path("all-strategy/", ListActiveStrategiesByAdminAPIView.as_view(), name="all_strategy"),
    path("strategies-dropdown/", ListStrategiesForDropdownAPIView.as_view(), name="strategies_dropdown"),
]
