from django.db import models


class Vendor(models.Model):
    """Database model for Vendors in the system"""
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    
    def __str__(self) -> str:
        return f"{self.name} -- {self.address}"


class ProductType(models.Model):
    """Database model for Product Types in the system"""
    p_type = models.CharField(max_length=155, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return self.p_type


class Product(models.Model):
    """Database model for Products in the system"""
    name = models.CharField(max_length=255)
    p_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    price = models.DecimalField(decimal_places=2, max_digits=10)
    quantity = models.IntegerField()
    created_date = models.DateField()
    
    def __str__(self) -> str:
        return self.name