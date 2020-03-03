from .models import Trade
from rest_framework import serializers
from v1.signals.serializers import SignalSerializer


class TradeSerializer(serializers.ModelSerializer):
    pair=serializers.StringRelatedField(read_only=True,source="signal.pair")
    action=serializers.StringRelatedField(read_only=True,source="signal.action")
    timeframe=serializers.StringRelatedField(read_only=True,source="signal.timeframe")
    signal_type=serializers.StringRelatedField(read_only=True,source="signal.generator.generator_type")
    class Meta:
        model=Trade
        fields=["id","pair","signal_type","action","risk","profit","stoploss_profit","timeframe","status"]
        extra_kwargs={"profit":{"read_only":True},"stoploss_profit":{"read_only":True},"status":{"read_only":True}}