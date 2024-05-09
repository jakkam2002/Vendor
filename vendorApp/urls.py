from django.urls import path
from .views import *

urlpatterns = [
    path('vendors/', VendorListCreateView.as_view(), name = 'vendor-retrieve-update-delete'),
    path('vendors/<int:pk>/', VendorRetrieveUpdateDeleteView.as_view(), name='purchase-order-list-create'),
    path('purchase_orders/', PurchaseOrderListCreateView.as_view(), name = 'purchase-order-retrievd-update-delete'),
    path('purchase_orders/<int:pnk>', PurchaseOrderRetrieveUpdateDeleteView.as_view(), name = 'purchase-order-retrieve-update-delete'),
    path('vendors/<int:pk>//performance/', VendorPerformanceView.as_view(), name = 'vendor-perfoemance'),
    path('purchase_orders/<int:pk>/acknowledge/', AcknowledgePurchaseOrderView.as_view(), name = 'acknowledge-purchase-order'),
]