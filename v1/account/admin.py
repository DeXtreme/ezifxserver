from django.contrib import admin
from .models import Account,Deposit,Withdrawal,PendingWithdrawal,PendingDeposit

admin.site.register(Account)
admin.site.register(Deposit)
admin.site.register(PendingDeposit)
admin.site.register(Withdrawal)
admin.site.register(PendingWithdrawal)