from django.db import models
from rent.models import RentAgreement

class Payment(models.Model):
    agreement = models.ForeignKey(RentAgreement, on_delete=models.CASCADE)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(auto_now_add=True)
    payment_mode = models.CharField(max_length=50, choices=[('Cash', 'Cash'), ('Bank Transfer', 'Bank Transfer')])
    receipt_number = models.CharField(max_length=100, unique=True)
    
    start_month = models.DateField()  # Payment covers from this date
    end_month = models.DateField()  # Payment covers till this date

    def save(self, *args, **kwargs):
        """ Updates total paid and recalculates remaining due when a payment is made """
        super().save(*args, **kwargs)
        self.agreement.total_paid += self.amount_paid
        self.agreement.calculate_due()  # Recalculate remaining due

    def __str__(self):
        return f"Payment {self.receipt_number} - {self.amount_paid}"
