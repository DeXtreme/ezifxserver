from rest_framework import serializers
from rest_framework import validators
from django.db import IntegrityError
from django.contrib.auth.models import User
from .models import Account,PendingDeposit,PendingWithdrawal

class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model=PendingDeposit
        fields=["amount","deposit_type","time"]

class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model=PendingWithdrawal
        fields=["amount","withdrawal_type","phone","time"]


class AccountSerializer(serializers.ModelSerializer):
    deposits=DepositSerializer(many=True,read_only=True,source="pending_deposits")
    withdrawals=WithdrawalSerializer(many=True,read_only=True,source="pending_withdrawals")
    class Meta:
        model=Account
        fields=['name','phone','email','account_type','balance','deposits',"withdrawals"]
        extra_kwargs = {'created': {'write_only': True}}

class UserSerializer(serializers.ModelSerializer):
    account=AccountSerializer(required=True,many=False)

    def create(self,data):
        try:
            user=User.objects.create_user(data["username"],password="defaultpass")
            Account.objects.create(user=user,**data["account"])
            return user
        except IntegrityError:
            raise validators.ValidationError({"detail":"Identity token error"})
    

    class Meta:
        model=User
        fields=['id','username','account']
        extra_kwargs = {'username': {'write_only': True}}


