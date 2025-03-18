from rest_framework import serializers
from rent.models import RentAgreement,Installment,Billboard,Landlord


# class RentAgreementSerializer(serializers.ModelSerializer):
#     remaining_due = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
#     last_paid_month = serializers.DateField(read_only=True)
#     next_payable_month = serializers.DateField(read_only=True)
#     class Meta:
#         model = RentAgreement
#         fields = '__all__'  # Include all fields



class DateFormatterMixin:
    """Mixin to format date fields as 'Month Year' (e.g., 'March 2025')"""
    
    def format_date(self, date):
        return date.strftime("%B %Y") if date else None


class InstallmentSerializer(serializers.ModelSerializer, DateFormatterMixin):
    billboard_hid = serializers.CharField(source="rent_agreement.billboard.hid", read_only=True)
    billboard_city = serializers.CharField(source="rent_agreement.billboard.city", read_only=True)
    billboard_width = serializers.DecimalField(source="rent_agreement.billboard.width", max_digits=5, decimal_places=2, read_only=True)
    billboard_height = serializers.DecimalField(source="rent_agreement.billboard.height", max_digits=5, decimal_places=2, read_only=True)

    landlord_name = serializers.CharField(source="rent_agreement.landlord.name", read_only=True)
    landlord_phone = serializers.CharField(source="rent_agreement.landlord.phone", read_only=True)

    agreement_number = serializers.CharField(source="rent_agreement.agreement_number", read_only=True)

    # Custom formatted date fields
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    month = serializers.SerializerMethodField()

    class Meta:
        model = Installment
        fields = [
            "id", "agreement_number", "start_date", "end_date", "billboard_hid", "billboard_city",
            "billboard_width", "billboard_height", "landlord_name", "landlord_phone",
            "month", "amount", "status", "rent_agreement"
        ]

    def get_start_date(self, obj):
        return self.format_date(getattr(obj.rent_agreement, "start_date", None))

    def get_end_date(self, obj):
        return self.format_date(getattr(obj.rent_agreement, "end_date", None))

    def get_month(self, obj):
        return self.format_date(getattr(obj, "month", None))


class RentAgreementSerializer(serializers.ModelSerializer, DateFormatterMixin):
    # import ipdb; ipdb.set_trace()
    billboard = serializers.PrimaryKeyRelatedField(queryset=Billboard.objects.all())  # Allow input
    # landlord = serializers.PrimaryKeyRelatedField(queryset=Landlord.objects.all())  # Allow input


    billboard_hid = serializers.CharField(source="billboard.hid", read_only=True)
    billboard_city = serializers.CharField(source="billboard.city", read_only=True)
    billboard_width = serializers.DecimalField(source="billboard.width", max_digits=5, decimal_places=2, read_only=True)
    billboard_height = serializers.DecimalField(source="billboard.height", max_digits=5, decimal_places=2, read_only=True)

    landlord_name = serializers.CharField(source="landlord.name", read_only=True)
    landlord_phone = serializers.CharField(source="landlord.phone", read_only=True)

    # Custom formatted date fields
    start_date = serializers.DateField()  # Allow input
    end_date = serializers.DateField()  # Allow input
    rent_increase_date = serializers.DateField(required=False, allow_null=True)


    class Meta:
        model = RentAgreement
        fields = [
            "id", "agreement_number", "start_date", "end_date","billboard","billboard_hid", "billboard_city",
            "billboard_width", "billboard_height", "landlord_name", "landlord_phone",
            "rent_amount_yearly", "payment_frequency_months", "total_paid", "remaining_due",
            "advance_amount", "rent_increase_date", "increase_amount", "created_at", "updated_at"
        ]

    def get_start_date(self, obj):
        return self.format_date(getattr(obj, "start_date", None))

    def get_end_date(self, obj):
        return self.format_date(getattr(obj, "end_date", None))

    def get_rent_increase_date(self, obj):
        return self.format_date(getattr(obj, "rent_increase_date", None))
