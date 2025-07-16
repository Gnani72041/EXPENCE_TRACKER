from django.db import models

class CurrentBalance(models.Model):
    current_balance= models.FloatField(default=0)

# Create your models here.
class TrackingHistory(models.Model):
    current_balance = models.ForeignKey(CurrentBalance, on_delete=models.CASCADE)
    amount = models.FloatField()
    expense_type = models.CharField(choices=(('CREDIT','CREDIT'),('DEBIT','DEBIT')),max_length=100)
    description = models.CharField(max_length=200)
    
    created_at=models.DateTimeField(auto_now_add=True)