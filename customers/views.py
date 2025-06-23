from .models import Customer
from django.utils import timezone
from .serializers import CustomerSerializer
from rest_framework.response import Response
from rest_framework import generics, status, permissions

class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class CustomerListView(generics.ListCreateAPIView):
    queryset = Customer.objects.filter(deleted_at__isnull=True)
    serializer_class = CustomerSerializer
    permission_classes = [IsAdmin]

class CurrentCustomerView(generics.RetrieveUpdateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.customer_profile

class CustomerDetailView(generics.RetrieveUpdateAPIView):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdmin]
    lookup_field = 'id'

class CustomerSoftDeleteView(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        instance.deleted_at = timezone.now()
        instance.save()

class CustomerRestoreView(generics.UpdateAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsAdmin]
    lookup_field = 'id'
    http_method_names = ['patch']

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = None
        instance.save()
        return Response(status=status.HTTP_200_OK)

class CustomerPermanentDeleteView(generics.DestroyAPIView):
    queryset = Customer.objects.all()
    permission_classes = [IsAdmin]
    lookup_field = 'id'

    def perform_destroy(self, instance):
        # Handle related objects if needed
        instance.delete()