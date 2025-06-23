from django.urls import path

from .views import (
    CustomerListView,
    CustomerDetailView,
    CurrentCustomerView,
    CustomerRestoreView,
    CustomerSoftDeleteView,
    CustomerPermanentDeleteView
)

urlpatterns = [
    path('', CustomerListView.as_view(), name='customer-list'),
    path('me/', CurrentCustomerView.as_view(), name='current-customer'),
    path('<uuid:id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('<uuid:id>/', CustomerSoftDeleteView.as_view(), name='customer-soft-delete'),
    path('<uuid:id>/restore/', CustomerRestoreView.as_view(), name='customer-restore'),
    path('<uuid:id>/force/', CustomerPermanentDeleteView.as_view(), name='customer-permanent-delete'),
]