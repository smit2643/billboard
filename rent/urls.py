from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rent.views import BillboardViewSet, LandlordViewSet, RentAgreementViewSet, PaymentViewSet,InstallmentViewSet,generate_pdf

router = DefaultRouter()
router.register(r'billboards', BillboardViewSet)
router.register(r'landlords', LandlordViewSet)
router.register(r'rent-agreements', RentAgreementViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'installments', InstallmentViewSet)

urlpatterns = [
    path('', include(router.urls)),
     path('generate-pdf/<int:rent_agreement_id>/', generate_pdf, name='generate_pdf'),
]
