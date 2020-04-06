from django.shortcuts import render,get_object_or_404
from django.http import Http404
from rest_framework.authentication import BaseAuthentication,TokenAuthentication
from rest_framework.permissions import BasePermission,IsAuthenticated
from rest_framework import exceptions
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,ListModelMixin
from rest_framework.response import Response
from .requests import getMarketInfo
from rest_framework import status
from django.conf import settings
from .models import SignalGenerator,Signal
from .serializers import SignalSerializer
from datetime import datetime
from rest_framework.pagination import BasePagination
from efxapi.permissions import MarketPermission

class GeneratorAuthentication(BaseAuthentication):
    def authenticate(self,request):
        token=request.META.get("HTTP_AUTHORIZATION")
        if(not token):
            return None
        
        try:
            token=token.split(" ")[1]
            generator=get_object_or_404(SignalGenerator,token=token)
        except:
            raise exceptions.AuthenticationFailed("Invalid token")
        
        return (generator,token)
    
    def authenticate_header(self,request):
        return "Token"

class GeneratorPermission(BasePermission):
    def has_permission(self,request,view):
        return bool(request.user and request.auth)


class SignalPagination(BasePagination):
    
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


class SignalsViewset(GenericViewSet,CreateModelMixin,ListModelMixin,RetrieveModelMixin):
    serializer_class=SignalSerializer
    authentication_classes=()
    queryset=Signal.objects.all()
    permission_classes=()
    pagination_class=SignalPagination

    #get_authenticators is called before .action is set so check the request method
    def get_authenticators(self):
        if(self.request.method.lower()=="post"):
            authentication_classes=[GeneratorAuthentication]
        else:
            authentication_classes=[TokenAuthentication]
        return [authenticator() for authenticator in authentication_classes]
    
    def get_permissions(self):
        if(self.action == "create"):
            permission_classes=[GeneratorPermission]
        else:
            permission_classes=[IsAuthenticated,MarketPermission]
        return [permission() for permission in permission_classes]


    def get_queryset(self):
        #error here
        account=self.request.user.account
        #return Signal.objects.all()
        if(account.account_type=="PR"):
            return Signal.objects.filter(expiry__gt=datetime.utcnow())
        else:
            return Signal.objects.filter(generator__generator_type="RG",expiry__gt=datetime.utcnow())

    
    def create(self,request):
        generator=request.user
        data=request.data.copy()
        #generator=SignalGenerator.objects.get(id=1)
        serializer=SignalSerializer(data=data)
        if(serializer.is_valid(raise_exception=True)):
            serializer.save(generator=generator)
            return Response(serializer.data)

    def retrieve(self,request,pk):
        try:
            signal=get_object_or_404(self.get_queryset(),id=pk)
            info=getMarketInfo(signal)
            signal_info={"id":info["id"],"min":info["min_risk"],"max":info["max_risk"],"close_time":info["close_time"],"open_time":info["open_time"],"fee":settings.FEE}
            return Response(signal_info)
        except Http404:
            return Response({"detail":"Signal has expired"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
           return Response({"detail":str(e) if str(e) else "Trades cannot be placed at the moment.Please try again later"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
