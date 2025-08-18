from django.urls import path
from .views import (
   StartStrategyAPIView, 
   CreateStrategyWithConditionsAPIView,
   ListActiveStrategiesByAdminAPIView,
   StopStrategyAPIView,
   StrategyStatusAPIView,
   ListStrategiesForDropdownAPIView,
   DeleteStrategyAPIView,
   GetStrategyByIdAPIView,
   UpdateStrategyByIdAPIView,
   SetStrategyActiveStatusAPIView,
   get_strategy_payload
   
)

urlpatterns = [
    path("create-strategy-with-conditions/", CreateStrategyWithConditionsAPIView.as_view(), name = 'create_strategy_with_conditions'),
    path("start-strategy/", StartStrategyAPIView.as_view(), name="start_strategy"),
    path("stop-strategy/<str:strategy_id>", StopStrategyAPIView.as_view(), name="stop_strategy"),
    path("strategy-status/<str:strategy_id>", StrategyStatusAPIView.as_view(), name="strategy_status"),
    path("all-strategy/", ListActiveStrategiesByAdminAPIView.as_view(), name="all_strategy"),
    path("strategies-dropdown/", ListStrategiesForDropdownAPIView.as_view(), name="strategies_dropdown"),
    path("delete-strategy/", DeleteStrategyAPIView.as_view(), name="delete_strategy"),
    path("get-strategy/<str:strategy_id>/", GetStrategyByIdAPIView.as_view(), name="get_strategy"),
    path("update-strategy/<str:strategy_id>/", UpdateStrategyByIdAPIView.as_view(), name="update_strategy"),
    path('set-status/', SetStrategyActiveStatusAPIView.as_view(), name='set-strategy-status'),
    path('get_strategy_payload/', get_strategy_payload.as_view(), name='set-strategy-status')
]
