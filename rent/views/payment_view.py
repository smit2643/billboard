from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rent.models import  Payment
from rent.serializers import PaymentSerializer



class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request, *args, **kwargs):
        """ Overriding create method to handle payments and update agreement dynamically """
        response = super().create(request, *args, **kwargs)
        payment = Payment.objects.get(id=response.data['id'])
        payment.agreement.calculate_due()
        return Response({"message": "Payment recorded", "remaining_due": payment.agreement.remaining_due})
