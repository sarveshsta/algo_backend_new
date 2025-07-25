# Generated by Django 4.2.7 on 2025-06-26 16:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('strategy', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='strategycondition',
            old_name='candle_count',
            new_name='left_candle_count',
        ),
        migrations.RemoveField(
            model_name='strategycondition',
            name='field',
        ),
        migrations.RemoveField(
            model_name='strategycondition',
            name='value',
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='comparison_type',
            field=models.CharField(choices=[('ohlc_vs_ohlc', 'OHLC Compare'), ('ohlc_vs_indicator', 'OHLC With Indicator'), ('indicator_vs_indicator', 'Indicator vs Indicator'), ('indicator_vs_value', 'Single Indicator')], default=django.utils.timezone.now, max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='constant_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='left_candle_offset',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='left_factor',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='left_indicator',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='left_multiplier',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='left_ohlc',
            field=models.CharField(blank=True, choices=[('open', 'Open'), ('high', 'High'), ('low', 'Low'), ('close', 'Close')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='logic_operator',
            field=models.CharField(blank=True, choices=[('AND', 'AND'), ('OR', 'OR')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_candle_count',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_candle_offset',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_factor',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_indicator',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_multiplier',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='strategycondition',
            name='right_ohlc',
            field=models.CharField(blank=True, choices=[('open', 'Open'), ('high', 'High'), ('low', 'Low'), ('close', 'Close')], max_length=10, null=True),
        ),
    ]
