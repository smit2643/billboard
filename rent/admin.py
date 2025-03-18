from django.contrib import admin
from .models import Billboard, Landlord, RentAgreement, Payment,Installment

@admin.register(Billboard)
class BillboardAdmin(admin.ModelAdmin):
    list_display = ('hid', 'landlord', 'city', 'district', 'area', 'width', 'height', 'created_at', 'updated_at')
    search_fields = ('hid', 'city', 'district', 'area')
    list_filter = ('city', 'district', 'created_at', 'updated_at')
    ordering = ('-created_at',)

@admin.register(Landlord)
class LandlordAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'billboard_count', 'created_at', 'updated_at')
    search_fields = ('name', 'email', 'phone')
    list_filter = ('created_at', 'updated_at')
    ordering = ('-created_at',)


@admin.register(RentAgreement)
class RentAgreementAdmin(admin.ModelAdmin):
    list_display = ('agreement_number', 'billboard', 'start_date', 'end_date', 
                    'rent_amount_yearly', 'payment_frequency_months', 'total_paid', 
                    'remaining_due', 'rent_increase_date', 'increase_amount', 
                    'created_at', 'updated_at')

    search_fields = ('billboard__id', 'landlord__name', 'agreement_number')
    list_filter = ('payment_frequency_months', 'rent_increase_date', 'created_at', 'updated_at')
    ordering = ('-created_at', 'start_date')

    readonly_fields = ('remaining_due', 'created_at', 'updated_at')  # Prevent manual editing

    actions = ['recalculate_due']

    def recalculate_due(self, request, queryset):
        """ Custom admin action to recalculate due amount for selected agreements """
        for agreement in queryset:
            agreement.calculate_due()
        self.message_user(request, "Due amounts recalculated successfully.")

    recalculate_due.short_description = "Recalculate Due Amount for Selected Agreements"


# @admin.register(Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ('agreement', 'amount_paid', 'payment_date', 'payment_mode', 'receipt_number', 
#                     'start_month', 'end_month')
    
#     search_fields = ('agreement__billboard__hid', 'agreement__landlord__name', 'receipt_number')
#     list_filter = ('payment_mode', 'payment_date')
#     ordering = ('-payment_date',)

#     readonly_fields = ('payment_date',)  # Prevent manual editing of auto-added fields

#     actions = ['recalculate_due']

#     def recalculate_due(self, request, queryset):
#         """ Custom admin action to recalculate due amount for selected payments """
#         for payment in queryset:
#             payment.agreement.calculate_due()
#         self.message_user(request, "Due amounts recalculated successfully.")
    
#     recalculate_due.short_description = "Recalculate Due Amount for Selected Payments"





@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = ('rent_agreement', 'formatted_month', 'amount','status')
    list_filter = ('month','status',)
    search_fields = ('rent_agreement__agreement_number',)
    ordering = ('id',)