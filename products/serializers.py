from rest_framework import serializers

from products.models import Product, Brand


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    """ Transforms model in json and vice-versa """

    class Meta:
        model = Product
        fields = ['url', 'sku', 'name', 'price', 'brand', 'visits']


class BrandSerializer(serializers.HyperlinkedModelSerializer):
    """ Transforms model in json and vice-versa """

    class Meta:
        model = Brand
        fields = ['url', 'name']
