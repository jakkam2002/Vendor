from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Avg
from django.db.models import F
from django.db import models
from django.utils import timezone

# Create your models here.
class Vendor(models.Model):
    name = models.CharField(max_length=225)
    contcat_details = models.TextField()
    address = models.TextField()
    vendor_code = models.CharField(max_length=50, unique=True, primary_key=True)
    on_time_delivery_rate = models.FloatField(default = 0)
    quality_rating_avg = models.FloatField(default = 0)
    average_response_time = models.FloatField(default = 0)
    fulfillment_rate = models.FloatField(default = 0)

    def __str__(self):
        return self.name
    
class PurchaseOrder(models.Model):
    po_number = models.CharField(max_length = 50, unique = True, primary_key = True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    delivery_date = models.DateTimeField(null=True, blank=True)
    delivered_data = models.DateTimeField(null=True, blank=True)
    items = models.JSONField
    quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=20)
    quality_rating = models.FloatField(null=True, blank=True)
    issue_date = models.DateTimeField()
    acknowledgement_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.po_number
class HistoricalPerformance(models.Model):
    vendor = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    date = models.DateTimeField()
    on_time_delivery_rate = models.FloatField()
    quality_rating_avg = models.FloatField()
    avergare_response_time = models.FloatField()
    fulfillment_rate = models.FloatField()
@receiver(post_save, sender = PurchaseOrder)
def update_vendor_performance(sender, instance, **kwargs):
    if instance.status == 'completed' and instance.delivered_data is None:
        instance.delivered_data = timezone.now()
        instance.save()
    
    #update on-time delivery rate
    completed_orders = PurchaseOrder.objects.filter(vendor = instance.vendor, status = 'completed')
    #on_time_delivery_rate = completed_orders.filter(delivery_date_lte = instance.delivery_date).count()
    on_time_deliveries = completed_orders.filter(delivery_date_gte = F('delivered_data'))
    on_time_delivery_rate = on_time_deliveries.count() / completed_orders.count()
    instance.vendor.on_time_delivery_rate = on_time_delivery_rate if on_time_delivery_rate else 0

    #Update Quality Rating Average
    completed_orders_with_rating = completed_orders.exclude(quality_rating_isnull=True)
    quality_rating_avg = completed_orders_with_rating.aggregrate(Avg('quality_rating'))['quality_rating_avg'] or 0
    instance.vendor.quality_rating_avg = quality_rating_avg if quality_rating_avg else 0
    instance.vendor.save()
@receiver(post_save, sender=PurchaseOrder)
def update_response_time(sender, instance, **kwargs):
    if instance.acknowledgement_date:
        #Update Average Response Time
        response_times = PurchaseOrder.objcets.filter(vendor=instance.vendor, acknowledgement_data_isnull = False).values_list('acknowledgement_date','issue_date')
        avergae_response_time = sum((ack_date - issue_date).total_seconds() for ack_date, issue_date in response_times) #/ len(response_times)
        if avergae_response_time < 0:
            avergae_response_time = 0
        if response_times:
            avergae_response_time = avergae_response_time / len(response_times)
        else:
            avergae_response_time = 0 #Avoid division by zero if there are no respnse times
        instance.vendor.average_response_time = avergae_response_time
        instance.vendor.save()
@receiver(post_save, sender = PurchaseOrder)
def update_fulfillment_rate(sender, instance, **kwargs):
    #Update Fulfillment Rtae
    fulfilled_orders = PurchaseOrder.objects.filter(vendor = instance.vendor, status = 'completed') #quality_rating_isnull = False
    fulfillment_rate = fulfilled_orders.count() / PurchaseOrder.objects.filter(vendor=instance.vendor).count()
    instance.vendor.fulfillment_rate = fulfillment_rate
    instance.vendor.save()




