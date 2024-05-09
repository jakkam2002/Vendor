from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import *
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Avg
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

# Create your views here.
class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
class VendorRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class =PurchaseOrderSerializer
class PurchaseOrderRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class =PurchaseOrderSerializer
class VendorPerformanceView(generics.RetrieveAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'on_time_delivery_rate':serializer.data['on_time_delivery_rate'],
                         'quality_rating_avg': serializer.data['quality_rating_avg'],
                         'avergae_response_time' : serializer.data['avergae_response_time'],
                         'fulfillment_rate' : serializer.data['fulfillment_rate']})
class AcknowledgePurchaseOrderView(generics.UpdateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.acknowledgement_date = request.data.get('acknowledgement_date')
        instance.save()
        response_times = PurchaseOrder.objects.filter(vendor=instance.vemdor, acknowledgement_date_isnull = False).values_list('acknowledgement_date', 'issue_date')
        average_response_time = sum(abs((ack_date - issue_date).total_seconds()) for ack_date, issue_date in response_times)
        if response_times:
            avergae_response_time = total_seconds / len(response_times)
        else:
            avergae_response_time = 0
        instance.vendor.average_response_time = average_response_time
        instance.vendor.save()
        return Response({'acknowledgement_date' : instance.acknowledgement_date})

