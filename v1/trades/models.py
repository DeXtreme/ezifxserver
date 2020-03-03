from django.db import models
from v1.signals.models import Signal
from django.contrib.auth.models import User

class Trade(models.Model):

    status_choices=[("O","Open"),("C","Closed"),("PO","Pending_Open"),("PC","Pending_Close"),("AO","Attempted_Open"),("AC","Attempted_Close"),("E","Error")]

    signal=models.ForeignKey(Signal,models.DO_NOTHING,related_name="trades")
    user=models.ForeignKey(User,models.DO_NOTHING,related_name="trades")
    trade_id=models.BigIntegerField(null=True) 
    lot_size=models.FloatField(null=True)
    risk=models.FloatField()
    stoploss=models.FloatField(null=True)
    stoploss_price=models.FloatField(null=True)
    current_price=models.FloatField(null=True) #used to track either bid or ask depending on trade type
    previous_price=models.FloatField(null=True) #used to track either bid or ask depending on trade type  
    profit=models.FloatField(null=True)
    stoploss_profit=models.FloatField(null=True)
    status=models.CharField(max_length=3,choices=status_choices)
    time=models.DateTimeField(auto_now=True)
