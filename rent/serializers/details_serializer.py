from rest_framework import serializers
from rent.models import Billboard, Landlord

class BillboardSerializer(serializers.ModelSerializer):
    landlord_name = serializers.CharField(source="landlord.name", read_only=True)
    landlord_phone = serializers.CharField(source="landlord.phone", read_only=True)

    class Meta:
        model = Billboard
        fields = [
            "id", "hid",  "landlord_name", "landlord_phone","district", "city", "area", "location", "width", "height", 
            "created_at", "updated_at"
        ]
        
class LandlordSerializer(serializers.ModelSerializer):
    billboard_count = serializers.SerializerMethodField()

    class Meta:
        model = Landlord
        fields = ['id', 'name', 'email', 'phone', 'address', 'remark', 'billboard_count']
    
    def get_billboard_count(self, obj):
        return obj.billboards.count()  # Ensure a related_name='billboards' in the model
    
    def validate(self, data):
        """Ensure name and phone are provided"""
        if 'name' not in data or not data['name'].strip():
            raise serializers.ValidationError({"name": "This field is required."})
        if 'phone' not in data or not data['phone'].strip():
            raise serializers.ValidationError({"phone": "This field is required."})
        return data
