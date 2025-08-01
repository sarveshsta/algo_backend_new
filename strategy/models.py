import uuid
from django.db import models
from algo_app.models import User



class Strategy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class StrategyCondition(models.Model):


    CONDITION_TYPE_CHOICES = [
        ('pre_buy', 'Pre Buy'),
        ('buy', 'Buy'),
        ('pre_sell', 'Pre Sell'),
        ('sell', 'Sell'),
        ('stop_loss', 'Stop Loss'),
        ('target', 'Target'),
    ]

    COMPARISON_TYPE_CHOICES = [
        ('spot', 'Spot'),  # For immediate execution after pre-condition
        ('ohlc_vs_ltp', 'OHLC vs LTP'),  # LTP compared to OHLC
        ('ohlc_vs_ohlc', 'OHLC Compare'),
        ('ohlc_vs_indicator', 'OHLC With Indicator'),
        ('indicator_vs_indicator', 'Indicator vs Indicator'),
        ('indicator_vs_value', 'Single Indicator'),
    ]

    OPERATOR_CHOICES = [
        ('<', '<'),
        ('<=', '<='),
        ('>', '>'),
        ('>=', '>='),
        ('==', '=='),
        ('!=', '!='),
    ]

    OHLC_CHOICES = [
        ('open', 'Open'),
        ('high', 'High'),
        ('low', 'Low'),
        ('close', 'Close'),
    ]

    LOGIC_OPERATOR_CHOICES = [
        ('AND', 'AND'),
        ('OR', 'OR'),
    ]

    VALUE_TYPE_CHOICES = [
        ('percent', 'Percentage'),
        ('points', 'Points'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    strategy = models.ForeignKey('Strategy', on_delete=models.CASCADE)

    # Defines the type of condition (pre_buy, buy, sell, stop_loss, target)
    type = models.CharField(max_length=20, choices=CONDITION_TYPE_CHOICES)

    # Defines how to compare (spot, ohlc_vs_ltp, etc.)
    comparison_type = models.CharField(max_length=32, choices=COMPARISON_TYPE_CHOICES)

    # Operator (>, <, etc.)
    operator = models.CharField(max_length=3, choices=OPERATOR_CHOICES)

    # OHLC vs OHLC / OHLC vs LTP
    left_ohlc = models.CharField(max_length=10, choices=OHLC_CHOICES, null=True, blank=True)
    left_multiplier = models.FloatField(null=True, blank=True)
    left_candle_offset = models.PositiveIntegerField(null=True, blank=True)

    right_ohlc = models.CharField(max_length=10, choices=OHLC_CHOICES, null=True, blank=True)
    right_multiplier = models.FloatField(null=True, blank=True)
    right_candle_offset = models.PositiveIntegerField(null=True, blank=True)

    # Indicator fields
    left_indicator = models.CharField(max_length=20, null=True, blank=True)
    left_factor = models.FloatField(null=True, blank=True)
    left_candle_count = models.PositiveIntegerField(null=True, blank=True)

    right_indicator = models.CharField(max_length=20, null=True, blank=True)
    right_factor = models.FloatField(null=True, blank=True)
    right_candle_count = models.PositiveIntegerField(null=True, blank=True)

    # Comparison to constant value (indicator_vs_value)
    constant_value = models.FloatField(null=True, blank=True)

    # For combining multiple conditions
    logic_operator = models.CharField(max_length=10, choices=LOGIC_OPERATOR_CHOICES, null=True, blank=True)

    # For target/stop_loss: specify if it's in percent or points
    value_type = models.CharField(max_length=10, choices=VALUE_TYPE_CHOICES, null=True, blank=True)

    # For target/stop_loss: value of SL/Target
    sl_tp_value = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.type} - {self.comparison_type}"


