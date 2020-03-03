from django.db import models
import datetime
import binascii
import os

class SignalGenerator(models.Model):
    generator_type_choices=[("RG","Regular"),("PR","Premium")]

    name=models.CharField(max_length=100)
    generator_type=models.CharField(max_length=5,choices=generator_type_choices,default="R")
    token=models.CharField(max_length=100,help_text="Auto generated",blank=True,editable=True) #TODO:change editable to False

    def save(self,*args,**kwargs):
        token=binascii.hexlify(os.urandom(20)).decode()
        while(SignalGenerator.objects.filter(token=token).exists()):
            token=binascii.hexlify(os.urandom(20)).decode()
        self.token=token
        return super().save(*args,**kwargs)
    

class Signal(models.Model):
    action_choices=[("BY","Buy"),("SL","Sell")]
    timeframe_choice=[("D1","1Day"),("H4","4Hour"),("H1","1Hour"),("M30","30Minutes"),("M15","15Minutes")]

    pair=models.CharField(max_length=7)
    action=models.CharField(max_length=3,choices=action_choices)
    timeframe=models.CharField(max_length=4,choices=timeframe_choice)
    bars=models.TextField()
    atr=models.FloatField()
    min_lot=models.FloatField()
    #is_jpy for jpy trades
    generator=models.ForeignKey(SignalGenerator,models.SET_NULL,related_name="signals",null=True)
    time=models.DateTimeField(auto_now=True)
    expiry=models.DateTimeField() 

    def save(self,*args,**kwargs):
        expiry_delta=datetime.timedelta()
        if(self.timeframe=="D1"):
            expiry_delta=datetime.timedelta(days=1)
        elif(self.timeframe=="H4"):
            expiry_delta=datetime.timedelta(hours=4)
        elif(self.timeframe=="H1"):
            expiry_delta=datetime.timedelta(hours=1)
        elif(self.timeframe=="M30"):
            expiry_delta=datetime.timedelta(minutes=30)
        elif(self.timeframe=="M15"):
            expiry_delta=datetime.timedelta(minutes=15)
        self.expiry=datetime.datetime.now()+expiry_delta
        return super().save(*args,**kwargs)
