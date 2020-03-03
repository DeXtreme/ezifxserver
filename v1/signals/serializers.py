from rest_framework import serializers
from .models import Signal,SignalGenerator
from rest_framework import status
import json


class SignalSerializer(serializers.ModelSerializer):
    
    signal_type=serializers.StringRelatedField(read_only=True,source="generator.generator_type")
    bars=serializers.JSONField(required=True)

    def validate_bars(self,points):
        if isinstance(points,list) and len(points)>0:
            for point in points:
                if(isinstance(point,float)):
                    continue
                else:
                    raise serializers.ValidationError(str(points))
        else:
            raise serializers.ValidationError("Invalid json format")
        return points
        
    class Meta:
        model=Signal
        #is expiry neccesary client side
        fields=['id','pair','signal_type','action','timeframe','bars','atr','min_lot','time','expiry']
        extra_kwargs={'expiry': {'read_only':True},'atr': {'write_only':True},'min_lot': {'write_only':True},}
