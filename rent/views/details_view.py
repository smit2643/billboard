from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.utils import timezone
from rent.models import Billboard, Landlord, RentAgreement, Payment
from rent.serializers import BillboardSerializer, LandlordSerializer


def check_required_fields(required_fields, request_data):    
    missing_fields = [field for field in required_fields if field not in request_data or not request_data[field]]

    if missing_fields:
        missing_fields_str = ", ".join(missing_fields)
        return f"{missing_fields_str} is required."
    return None


class LandlordViewSet(viewsets.ModelViewSet):
    queryset = Landlord.objects.all()
    serializer_class = LandlordSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            ordering = request.GET.get('ordering', 'id')
            queryset = queryset.order_by(ordering)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True, context={'request': request})
                serialized_data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.serializer_class(queryset, many=True, context={'request': request})
                serialized_data = serializer.data

            count = queryset.count()
            limit = int(request.GET.get('page_size', 10))  
            current_page = int(request.GET.get('page', 1)) 
            # serializer = self.get_serializer(queryset, many=True)
            response_data={
                "status": True,
                "message": "Landlords retrieved successfully.",
                'total_page': (count + limit - 1) // limit,
                'count': count,
                'current_page': current_page,
                'data': serialized_data['results'] if 'results' in serialized_data else serialized_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            required_fields = ['name','phone']
            error_message = check_required_fields(required_fields, request.data)
            
            if error_message:
                return Response({"status": False, "message": error_message}, status=status.HTTP_400_BAD_REQUEST)
         
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True, "message": "Landlord added successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"status": False, "message": "Validation error!", "error_details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to retrieve landlord.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=timezone.now())
            return Response({"status": True, "message": "Landlord updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to update landlord.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"status": True, "message": "Landlord deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to delete landlord.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BillboardViewSet(viewsets.ModelViewSet):
    queryset = Billboard.objects.all()
    serializer_class = BillboardSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            ordering = request.GET.get('ordering', 'id')
            queryset = queryset.order_by(ordering)

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.serializer_class(page, many=True, context={'request': request})
                serialized_data = self.get_paginated_response(serializer.data).data
            else:
                serializer = self.serializer_class(queryset, many=True, context={'request': request})
                serialized_data = serializer.data

            count = queryset.count()
            limit = int(request.GET.get('page_size', 10))  
            current_page = int(request.GET.get('page', 1)) 

            # serializer = self.get_serializer(queryset, many=True)
            response_data={
                "status": True,
                "message": "Billboards retrieved successfully.",
                'total_page': (count + limit - 1) // limit,
                'count': count,
                'current_page': current_page,
                'data': serialized_data['results'] if 'results' in serialized_data else serialized_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            required_fields = ['hid']
            error_message = check_required_fields(required_fields, request.data)
            
            if error_message:
                return Response({"status": False, "message": error_message}, status=status.HTTP_400_BAD_REQUEST)
    
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": True, "message": "Billboard added successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"status": False, "message": "Validation error!", "error_details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to retrieve billboard.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(updated_at=timezone.now())
            return Response({"status": True, "message": "Billboard updated successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to update billboard.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"status": True, "message": "Billboard deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to delete billboard.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)