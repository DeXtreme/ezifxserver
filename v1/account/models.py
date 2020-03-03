from django.db import models
from django.contrib.auth.models import User
import binascii
import os
import datetime

class Account(models.Model):

    account_type_choices=[("RG","Regular"),("PR","Premium"),("DM","Demo")]

    user=models.OneToOneField(User,related_name='account',on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    phone=models.CharField(max_length=15,blank=True,unique=True,null=True)
    email=models.EmailField(blank=True,unique=True,null=True)
    account_type=models.CharField(max_length=2,choices=account_type_choices,default="DM")
    balance=models.FloatField(default=0.0)
    expiry=models.DateField(blank=True,null=True) #Premium expiry date
    created=models.DateField(auto_now=True)

class Deposit(models.Model):

    type_choices=[("mtn","MTN"),("visa","Visa")]

    account=models.ForeignKey(Account,related_name="deposits",on_delete=models.DO_NOTHING)
    amount=models.FloatField()
    deposited=models.FloatField()
    deposit_type=models.CharField(max_length=10,choices=type_choices)
    time=models.DateTimeField(auto_now=True)


class PendingDeposit(models.Model):

    type_choices=[("mtn","MTN"),("visa","Visa")]

    account=models.ForeignKey(Account,related_name="pending_deposits",on_delete=models.DO_NOTHING)
    amount=models.FloatField()
    deposit_type=models.CharField(max_length=6,choices=type_choices)
    time=models.DateTimeField(auto_now=True)

class Withdrawal(models.Model):
    type_choices=[("mtn","MTN"),("voda","Vodafone")]

    account=models.ForeignKey(Account,related_name="withdrawals",on_delete=models.DO_NOTHING)
    amount=models.FloatField()
    withdrawn=models.FloatField()
    withdrawal_type=models.CharField(max_length=6,choices=type_choices)
    phone=models.CharField(max_length=12)
    time=models.DateTimeField(auto_now=True)


class PendingWithdrawal(models.Model):
    type_choices=[("mtn","MTN"),("voda","Vodafone")]

    account=models.ForeignKey(Account,related_name="pending_withdrawals",on_delete=models.DO_NOTHING)
    amount=models.FloatField()
    withdrawal_type=models.CharField(max_length=6,choices=type_choices)
    phone=models.CharField(max_length=12)
    time=models.DateTimeField(auto_now=True)
