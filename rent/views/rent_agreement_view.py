from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from rent.models import  RentAgreement,Installment
from rent.serializers import RentAgreementSerializer,InstallmentSerializer

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.utils import timezone
from rent.models import RentAgreement
from rent.serializers import RentAgreementSerializer
from decimal import Decimal
from datetime import datetime, date


from django.shortcuts import render
from django.http import HttpResponse
from weasyprint import HTML
from rent.models import Landlord, Billboard

def check_required_fields(required_fields, data):
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None

class RentAgreementViewSet(viewsets.ModelViewSet):
    queryset = RentAgreement.objects.all()
    serializer_class = RentAgreementSerializer

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
            
            response_data = {
                "status": True,
                "message": "Rent agreements retrieved successfully.",
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
            required_fields = ['agreement_number', 'billboard', 'landlord', 'start_date', 'end_date', 'rent_amount_yearly', 'payment_frequency_months']
            missing_fields = [field for field in required_fields if field not in request.data]
            
            if missing_fields:
                return Response({"status": False, "message": f"Missing fields: {', '.join(missing_fields)}"}, status=status.HTTP_400_BAD_REQUEST)

            rent_increase_date = request.data.get('rent_increase_date')
            increase_amount = request.data.get('increase_amount', 0)

            # If increase_amount is provided but no rent_increase_date, return an error
            if increase_amount and not rent_increase_date:
                return Response({"status": False, "message": "Increase amount is only allowed if rent increase date is provided."}, status=status.HTTP_400_BAD_REQUEST)
            billboard_id = request.data.get("billboard")

            if not Billboard.objects.filter(id=billboard_id).exists():
                return Response({"status": False, "message": "Invalid billboard ID."}, status=400)
            print("-------",request.data)
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                print(serializer)
                instance = serializer.save()
                print("=======",instance)
                 # Perform calculations after saving
                advance_amount = Decimal(request.data.pop('advance_amount', 0))  # Convert to Decimal
                increase_amount = Decimal(request.data.pop('increase_amount', 0)) if rent_increase_date else Decimal(0)

                instance.rent_amount_yearly += increase_amount  # Add increase amount to yearly rent
                instance.total_paid = advance_amount  # Set total paid as advance amount
                instance.remaining_due = instance.rent_amount_yearly -  instance.total_paid  # Calculate remaining due
                
                instance.save()  # Save updated instance
                print("************",instance)
                instance.generate_installments(instance.remaining_due)
                print("------------",instance)
                 # Serialize the updated instance including installments
                response_serializer = RentAgreementSerializer(instance)

                
                return Response({"status": True, "message": "Rent agreement added successfully.", "data":response_serializer.data}, status=status.HTTP_201_CREATED)
            
            return Response({"status": False, "message": "Validation error!", "error_details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                "status": True,
                "data": {
                    **serializer.data,
                 
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to retrieve rent agreement.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

  

    def update(self, request, *args, **kwargs):
        try:
            # import ipdb; ipdb.set_trace()
            instance = self.get_object()

            rent_increase_date = request.data.get('rent_increase_date')
            increase_amount = request.data.get('increase_amount', 0)
          
            if increase_amount and not rent_increase_date:
                return Response({"status": False, "message": "Increase amount is only allowed if rent increase date is provided."}, status=status.HTTP_400_BAD_REQUEST)

            old_advance_amount = Decimal(instance.advance_amount)              
            new_advance_amount = Decimal(request.data.get('advance_amount', 0))  
            
            other_payments = instance.total_paid - old_advance_amount        
          
            new_total_paid = Decimal(request.data.get('total_paid', instance.total_paid)) 


            if  request.data.get('advance_amount') == 0:
                updated_total_paid= new_total_paid -old_advance_amount
            elif new_advance_amount == 0:
                updated_total_paid = instance.total_paid if 'total_paid' not in request.data else new_total_paid
            else:
                updated_total_paid = new_advance_amount + other_payments if 'total_paid' not in request.data else new_total_paid


            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                updated_instance = serializer.save()  # Save the updated instance

                updated_instance.total_paid = updated_total_paid

                # Handle rent increase calculations
                rent_increase_date = updated_instance.rent_increase_date
                increase_amount = Decimal(request.data.get('increase_amount', 0)) if rent_increase_date else Decimal(0)
                increase_total_rent=updated_instance.rent_amount_yearly

                updated_instance.rent_amount_yearly += increase_amount

                # Update remaining due
                updated_instance.remaining_due = updated_instance.rent_amount_yearly - updated_instance.total_paid
                updated_instance.save()  # Save final calculations

                # Regenerate installments
                updated_instance.generate_installments(rent_amount=  updated_instance.remaining_due)

                # Serialize the updated instance including installments
                response_serializer = RentAgreementSerializer(updated_instance)
                return Response({"status": True, "message": "Rent agreement updated successfully.", "data":  response_serializer.data}, status=status.HTTP_200_OK)

            return Response({"status": False, "message": "Validation error!", "error_details": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"status": False, "message": "Something went wrong!", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    # def update_payment(self, request, *args, **kwargs):
    #     try:
    #         instance = self.get_object()
    #         amount_paid = request.data.get("amount_paid")

    #         if not amount_paid or float(amount_paid) <= 0:
    #             return Response({"status": False, "message": "Invalid payment amount."}, status=status.HTTP_400_BAD_REQUEST)

    #         instance.total_paid += float(amount_paid)
    #         instance.save()  # Auto-triggers calculations in serializer

    #         return Response({
    #             "status": True,
    #             "message": "Payment updated successfully.",
    #             "last_paid_month": instance.last_paid_month.strftime("%b %Y") if instance.last_paid_month else None,
    #             "next_payable_month": instance.next_payable_month.strftime("%b %Y") if instance.next_payable_month else None
    #         }, status=status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({"status": False, "message": "Failed to update payment.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class InstallmentViewSet(viewsets.ModelViewSet):
    queryset = Installment.objects.all()
    serializer_class = InstallmentSerializer

    def list(self, request, *args, **kwargs):
        try:
           
            rent_agreement = request.GET.get("rent_agreement")  # Get rent_agreement ID from params
        
            queryset = self.get_queryset()
            
            if rent_agreement:
                queryset = queryset.filter(rent_agreement=rent_agreement)  # Filter by rent_agreement

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

            response_data = {
                "status": True,
                "message": "Installments retrieved successfully.",
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
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid():
                new_installment = serializer.save()  # Save the new installment

                # Update the rent agreement details
                rent_agreement = new_installment.rent_agreement
                if new_installment.status:  # If installment is marked as paid
                    rent_agreement.total_paid += new_installment.amount

                # Update remaining due
                rent_agreement.remaining_due = rent_agreement.rent_amount_yearly - rent_agreement.total_paid
                rent_agreement.save()

                # Serialize the created instance
                response_serializer = InstallmentSerializer(new_installment)

                return Response({ "status": True,"message": "Installment created successfully.","data": response_serializer.data}, status=status.HTTP_201_CREATED)

            return Response({
                "status": False,
                "message": "Validation error!",
                "error_details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "status": False,
                "message": "Something went wrong!",
                "error_details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            old_status = instance.status
            old_amount =Decimal(instance.amount)

            # Ensure new_status is converted properly to boolean
            new_status = request.data.get('status', instance.status)
            new_amount = Decimal(request.data.get('amount', instance.amount))
            
            new_status = str(new_status).lower() in ["true", "1"]  # Convert to boolean

            print(f"Old Status (type={type(old_status)}): {old_status}")
            print(f"New Status (type={type(new_status)}): {new_status}")
            print(f"New amount  (type={type(new_amount)}): {new_amount}")
            print(f"old amount  (type={type(old_amount)}): {old_amount}")


            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                updated_instance = serializer.save()  # Save the updated installment
                rent_agreement = updated_instance.rent_agreement
              
           

                total_rent = Decimal(rent_agreement.remaining_due)

                if old_status is not new_status:    
                    # rent_agreement = updated_instance.rent_agreement
                    
                    if new_status:  # Mark as paid
                        rent_agreement.total_paid += updated_instance.amount
                    elif new_status is False:  # Mark as unpaid
                        print("Status changed to unpaid!")
                        rent_agreement.total_paid -= updated_instance.amount

                    # Update remaining due
                    rent_agreement.remaining_due = rent_agreement.rent_amount_yearly - rent_agreement.total_paid
                   
                    
                    rent_agreement.save()  # Save final calculations

                all_installments = rent_agreement.installments.order_by("month")
               
                installment_months = [installment.month for installment in all_installments]
                total_months = len(installment_months)
                print(f'total months:{total_months}')

                if new_amount is not old_amount:
                    # Find unpaid future installments
                    future_installments = all_installments.filter(
                        month__gt=instance.month,
                        status=False  # Adjust only unpaid installments
                    )
                    remaining_installments = future_installments.count()
                    print(f'remain months:{remaining_installments}')

                    if remaining_installments > 0:
                        past_installments = all_installments.filter(month__gt=instance.month,status=True)
                        print(f"pasi_instal ",past_installments)
                        
                        past_installment_amount = [installment.amount for installment in past_installments]
                        print(f"pass maount",past_installment_amount)
                        
                        total_past_amount = Decimal(sum(past_installment_amount))
                        print(f"total past amount",total_past_amount)

                        new_val= total_rent -total_past_amount -new_amount
                        print(f"new valu",new_val)

                        if new_val != 0:

                        # Ensure each installment adjustment is rounded to the nearest 100
                            per_installment_diff=new_val / remaining_installments
                            per_installment_adjustment = round(per_installment_diff / 100) * 100  

                            # Adjust future installments
                            rounded_values = [per_installment_adjustment] * remaining_installments
                            total_adjusted = sum(rounded_values)
                            
                            # Handle rounding discrepancy for the last installment
                            if total_adjusted != new_val:
                                last_adjustment = new_val - (sum(rounded_values[:-1]))  # Adjust last one to maintain total sum
                                last_adjustment = round(last_adjustment / 100) * 100  # Ensure it is a multiple of 100
                                rounded_values[-1] = last_adjustment

                            print(f"\n=== Adjusting Future Installments ===")
                            for inst, adjust_amount in zip(future_installments, rounded_values):
                                print(f"Updating Installment: {inst.month} -> {inst.amount - adjust_amount}")
                                inst.amount = adjust_amount  # Assign rounded amount
                                inst.save()
                                        
                response_serializer = InstallmentSerializer(updated_instance)
                return Response({
                    "status": True, 
                    "message": "Installment updated successfully.", 
                    "data": response_serializer.data,
                    "total paid": rent_agreement.total_paid,
                    "rent amount": rent_agreement.rent_amount_yearly,
                    "remaining":rent_agreement.remaining_due

                }, status=status.HTTP_200_OK)

            return Response({
                "status": False, 
                "message": "Validation error!", 
                "error_details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({
                "status": False, 
                "message": "Something went wrong!", 
                "error_details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


    def retrieve(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)

            return Response({
                "status": True,
                "message": "Installment retrieved successfully.",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to retrieve installment.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"status": True, "message": "Installment deleted successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": False, "message": "Failed to delete installment.", "error_details": str(e)}, status=status.HTTP_400_BAD_REQUEST)





def generate_pdf(request, rent_agreement_id):
    rent_agreement = RentAgreement.objects.get(id=rent_agreement_id)
   
    # Fetch related billboard and landlord
    billboard = rent_agreement.billboard
    landlord = billboard.landlord  # Get the landlord from the billboard

    # Fetch installments for the rent agreement
    installments = Installment.objects.filter(rent_agreement=rent_agreement)

    html_string = render(request, 'rent/document_template.html', {
        'landlord': landlord,
        'billboards': billboard,  # Pass all billboards related to the landlord
        'rent_agreement': rent_agreement,  
        'installments': installments
    }).content.decode("utf-8")

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="rent_agreement_{rent_agreement_id}.pdf"'
    return response
