from .models import Strategy, StrategyCondition
from rest_framework import serializers

class CreateStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ['name', 'description']


class StrategyConditionSerializer(serializers.ModelSerializer):
    # Make `operator` optional — we'll validate it manually
    operator = serializers.ChoiceField(
        choices=StrategyCondition.OPERATOR_CHOICES,
        required=False
    )
    comparison_type = serializers.ChoiceField(
        choices=StrategyCondition.COMPARISON_TYPE_CHOICES,
        required=False
    )

    class Meta:
        model = StrategyCondition
        fields = [
            "id",
            "strategy",
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
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, data):
        condition_type = data.get("type")
        comparison_type = data.get("comparison_type")

        # --- Validate stop_loss / target ---
        if condition_type in ["stop_loss", "target"]:
            if not data.get("value_type"):
                raise serializers.ValidationError({
                    "value_type": f"`value_type` is required for condition type `{condition_type}`"
                })
            if data.get("sl_tp_value") is None:
                raise serializers.ValidationError({
                    "sl_tp_value": f"`sl_tp_value` is required for condition type `{condition_type}`"
                })
            if comparison_type:
                raise serializers.ValidationError({
                    "comparison_type": f"`comparison_type` should not be set for condition type `{condition_type}`"
                })
            return data  # ✅ No further checks for SL/Target

        # --- Validate other condition types ---
        if comparison_type not in dict(StrategyCondition.COMPARISON_TYPE_CHOICES):
            raise serializers.ValidationError({
                "comparison_type": "Invalid comparison_type"
            })

        # Determine required fields based on comparison_type
        if comparison_type == "ohlc_vs_ohlc":
            required = ["left_ohlc", "right_ohlc", "left_multiplier", "right_multiplier", "left_candle_offset", "right_candle_offset"]
        elif comparison_type == "ohlc_vs_indicator":
            required = ["left_ohlc", "left_multiplier", "left_candle_offset", "right_indicator", "right_factor", "right_candle_count"]
        elif comparison_type == "indicator_vs_indicator":
            required = ["left_indicator", "left_factor", "left_candle_count", "right_indicator", "right_factor", "right_candle_count"]
        elif comparison_type == "indicator_vs_value":
            required = ["left_indicator", "left_factor", "left_candle_count", "constant_value"]
        elif comparison_type == "ohlc_vs_ltp":
            required = ["left_ohlc", "left_candle_offset"]
        elif comparison_type == "spot":
            required = []
        else:
            raise serializers.ValidationError({
                "comparison_type": f"Unhandled comparison_type `{comparison_type}`"
            })

        # Check for missing required fields
        missing = [field for field in required if data.get(field) in [None, ""]]
        if missing:
            raise serializers.ValidationError({
                "missing_fields": f"Missing required fields for `{comparison_type}`: {', '.join(missing)}"
            })

        # Require operator only for relevant comparison types
        if comparison_type not in ["spot"] and not data.get("operator"):
            raise serializers.ValidationError({
                "operator": f"`operator` is required for comparison type `{comparison_type}`"
            })

        return data


class StrategyExecutionInputSerializer(serializers.Serializer):
    strategy_id = serializers.CharField()
    index = serializers.CharField()
    expiry = serializers.CharField()
    strike_price = serializers.CharField()
    option_type = serializers.ChoiceField(choices=["CE", "PE"])
    quantity = serializers.IntegerField()
    trade_amount = serializers.FloatField()
    target_profit = serializers.FloatField()
    candle_duration = serializers.CharField()


class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = "__all__"

# serializers.py

class StrategyDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Strategy
        fields = ['id', 'name']
