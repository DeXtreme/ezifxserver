from django.db import models

class SocInfo(models.Model):
    account_id=models.CharField(max_length=10,blank=True,null=True)
    offers=models.CharField(max_length=1000,blank=True,null=True)
    socket_id=models.CharField(max_length=100)
