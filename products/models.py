
from django.db import models


class Brand(models.Model):
    """Brand names"""

    name = models.CharField(max_length=12)

    def __str__(self):
        return f"{self.name}"


class Product(models.Model):
    """Stores products"""

    sku = models.CharField(max_length=8, primary_key=True)
    name = models.CharField(max_length=32)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT)
    visits = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return f"{self.name} - {self.brand}: USD {self.price}"
