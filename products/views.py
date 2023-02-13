
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework import permissions

from products.managers import NotificationsManager
from products.models import Product, Brand
from products.serializers import ProductSerializer, BrandSerializer


class ProductViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows products to be viewed or edited.
    """
    queryset = Product.objects.all().order_by('sku')
    serializer_class = ProductSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]

    def retrieve(self, request, *args, **kwargs):
        """ Overrides default behaviour for anonymous users """

        if request.user.is_anonymous:
            queryset = Product.objects.all()
            product = get_object_or_404(queryset, pk=kwargs['pk'])
            product.visits += 1
            product.save()

        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """ Overrides default behaviour for anonymous users """
        self._notify_admins(request, kwargs['pk'])
        return super().update(request, *args, **kwargs)

    def _notify_admins(self, request, pk=None):
        if request.user.groups.filter(name='admin').exists():
            queryset = Product.objects.all()
            product = get_object_or_404(queryset, pk=pk)
            NotificationsManager.notify_admins(request.user, product)


class BrandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows brands to be viewed or edited.
    """
    queryset = Brand.objects.all().order_by('name')
    serializer_class = BrandSerializer
    permission_classes = [permissions.DjangoModelPermissionsOrAnonReadOnly]
