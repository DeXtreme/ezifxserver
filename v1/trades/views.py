from django.shortcuts import render,get_object_or_404
from django.http import Http404
from django.contrib.auth.models import User
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin,ListModelMixin,RetrieveModelMixin
from rest_framework import status
from rest_framework.pagination import BasePagination
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.exceptions import APIException,PermissionDenied
from rest_framework.permissions import IsAuthenticated
from .serializers import TradeSerializer
from .models import Trade
from v1.signals.models import Signal
from .requests import openTrade,closeTrade
from datetime import datetime
from efxapi.permissions import MarketPermission


class ClosedTradesPagination(BasePagination):
    
    def __init__(self):
        self.first_id=0
        self.last_id=0
        super().__init__

    def paginate_queryset(self, queryset, request, view=None):
        page_limit=10
        if("next" in request.query_params and request.query_params["next"]):
            temp_queryset=queryset.filter(id__gt=request.query_params["next"]).order_by("-id")[:page_limit]
        elif("prev" in request.query_params and request.query_params["prev"]):
            temp_queryset=queryset.filter(id__lt=request.query_params["prev"]).order_by("-id")[:page_limit]
        else:
            temp_queryset=queryset.order_by("-id")[:page_limit]
            
        return temp_queryset

    def get_paginated_response(self, data):
        return Response({
            'results': data
        })


class TradesViewset(GenericViewSet,CreateModelMixin,ListModelMixin,RetrieveModelMixin):
    serializer_class=TradeSerializer
    pagination_class=ClosedTradesPagination
    permission_classes=[IsAuthenticated,MarketPermission]
    

    def get_queryset(self):
        return Trade.objects.filter(user__username=self.request.user.username,status="C")
        if self.action=="list":
            return Trade.objects.filter(user__username=self.request.user.username,status="O")
        else:
            return Trade.objects.filter(user__username=self.request.user.username,status="C")

    
    def create(self,request):
        try:
            signal=get_object_or_404(Signal,id=request.data.get("signal"),expiry__gt=datetime.utcnow())
            user=request.user
            risk=request.data.get("risk")
            trade=openTrade(user,signal,risk)
            return Response(TradeSerializer(trade).data)
        except Http404:
            return Response({"details":"Signal has expired"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
           return Response({"details":str(e) if str(e) else "Trade could not be opened.Please try again later"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            

       

    #crate action or use delete?
    @action(detail=True,methods=["GET"])
    def close(self,request,pk):
        try:
            trade=get_object_or_404(Trade,id=pk,status="O",user__username=self.request.user.username)
            trade=closeTrade(trade)
            return Response(TradeSerializer(trade).data,status=status.HTTP_200_OK)
        except:   
            return Response({"details":"Trade could not be closed.Please try again later"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)