from django.db import models;
from rent.models import Billboard,Landlord
from django.utils import timezone
from dateutil.relativedelta import relativedelta
import uuid
from datetime import timedelta
from decimal import Decimal,ROUND_DOWN,ROUND_HALF_UP
from datetime import datetime, timedelta


class RentAgreement(models.Model):
    agreement_number = models.CharField(max_length=100, unique=True)
    billboard = models.ForeignKey('Billboard', on_delete=models.CASCADE)
    # landlord = models.ForeignKey('Landlord', on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()
    rent_amount_yearly = models.DecimalField(max_digits=10, decimal_places=2)
    payment_frequency_months = models.PositiveIntegerField(default=1)  # Default: 1 month

    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    remaining_due = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    rent_increase_date = models.DateField(null=True, blank=True)
    increase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

      
    def __str__(self):
        return f"{self.agreement_number} - {self.billboard} - ({self.start_date} to {self.end_date})"


    def save(self, *args, **kwargs):
        # Ensure total_paid never exceeds rent_amount_yearly
        increase_amount = self.increase_amount or Decimal("0.00")
        if self.total_paid > self.rent_amount_yearly + increase_amount:
            raise ValueError("Total paid cannot exceed the yearly rent amount!")

        # Ensure dates are stored as the first of the month only if they are not None
        if self.start_date is not None:
            self.start_date = self.start_date.replace(day=1)
        if self.end_date is not None:
            self.end_date = self.end_date.replace(day=1)
        if self.rent_increase_date is not None:
            self.rent_increase_date = self.rent_increase_date.replace(day=1)

        super().save(*args, **kwargs)  # Call the parent save method

    def generate_installments(self, rent_amount):
        print(f"\n=== Generating Installments for Agreement {self.agreement_number} ===")
        print(f"Rent Amount: {rent_amount}")
        
        existing_installments = {inst.month: inst for inst in self.installments.all()}  
        paid_installments = {inst.month: inst for inst in self.installments.filter(status=True)}  # Keep paid ones
        unpaid_installments = {inst.month: inst for inst in self.installments.filter(status=False)}  # Only update these
        print(f"Paid Installments: {paid_installments}")
        print(f"Unpaid Installments: {unpaid_installments}")

        print(f"Existing Installments: {existing_installments}")

        start_date = self.start_date
        end_date = self.end_date
        rent_increase_date = self.rent_increase_date
        increase_amount = Decimal(self.increase_amount or 0)

        print(f"Start Date: {start_date}, End Date: {end_date}, Rent Increase Date: {rent_increase_date}")
        print(f"Increase Amount: {increase_amount}")

        # Generate correct installment months based on frequency
        installment_months = []
        current_date = start_date

        while current_date <= end_date:
            month_offset = self.payment_frequency_months
            next_month = current_date.month + month_offset
            next_year = current_date.year + (next_month - 1) // 12
            next_month = (next_month - 1) % 12 + 1
            current_date = datetime(next_year, next_month, 1).date()

            if current_date <= end_date:
                installment_months.append(current_date)

        print(f"Generated Installment Months: {installment_months}")

        # Total rent calculations #total=20000,radvance is =4000,remaining is =16000 , paid is 8000,rmainindg is 8000,increase is 10000, remain is 18000
        total_rent = Decimal(rent_amount)  #8000
        total_months = len(installment_months) #jun,sept,dec,march
        print()
        if not rent_increase_date:
            base_amount = total_rent / total_months 
            rounded_amounts = [round(base_amount / 100) * 100] * total_months
        else:
            pre_increase_months = [m for m in installment_months if m < rent_increase_date] #jun,sept
            post_increase_months = [m for m in installment_months if m >= rent_increase_date] #dec,march
            print( f"pre increase month",pre_increase_months)
            print(f"post increase",post_increase_months)
            pre_months_count = len(pre_increase_months) #2
            post_months_count = len(post_increase_months) #2

            pre_remain = Decimal(total_rent) - Decimal(increase_amount) #8000

            pre_base_amount = pre_remain / total_months # month satus is
            pre_installments = [round(pre_base_amount / 100) * 100] * pre_months_count
            paid_amount = sum(pre_installments)

            remaining_rent = Decimal(total_rent) - Decimal(paid_amount)
 
            post_base_amount = remaining_rent / post_months_count
            post_installments = [round(post_base_amount / 100) * 100] * post_months_count

            rounded_amounts = pre_installments + post_installments

        print(f"Rounded Installment Amounts: {rounded_amounts}")

        # Adjust last installment to match the total
        total_rounded = sum(rounded_amounts)
        adjustment = (total_rent) - total_rounded
        adjustment = round(adjustment / 100) * 100
        rounded_amounts[-1] += adjustment

        print(f"Final Adjusted Amounts: {rounded_amounts}")

        # Create or update installments
        new_installment_set = set(installment_months)
        existing_installment_set = set(existing_installments.keys())

        for month in existing_installment_set - new_installment_set:
            print(f"Deleting Old Installment: {month}")
            existing_installments[month].delete()

        for month, amount in zip(installment_months, rounded_amounts):
            if month in existing_installments:
                print(f"Updating Installment: {month} -> {amount}")
                installment = existing_installments[month]
                installment.amount = amount
                installment.save()
            else:
                print(f"Creating Installment: {month} -> {amount}")
                Installment.objects.create(
                    rent_agreement=self,
                    month=month,
                    amount=amount
                )

        print("=== Installment Generation Completed ===\n")



    print("=== Installment Update Completed ===\n")
    def formatted_start_month(self):
        return self.start_date.strftime("%B %Y")  # "March 2025"

    def formatted_end_month(self):
        return self.end_date.strftime("%B %Y")  # "March 2026"
    






class Installment(models.Model):
    rent_agreement = models.ForeignKey(
        'RentAgreement', on_delete=models.CASCADE, related_name='installments'
    )
    month = models.DateField()  # Stored as YYYY-MM-01 (Always the first day of the month)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.BooleanField(default=False)  # Paid or Not Paid

    def formatted_month(self):
        """Return month in 'March 2025' format"""
        return self.month.strftime("%B %Y")

    def __str__(self):
        return f"{self.rent_agreement.agreement_number} - {self.formatted_month()} - ₹{self.amount}"
