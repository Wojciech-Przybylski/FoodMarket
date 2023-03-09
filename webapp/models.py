from django.db import models
from django.utils import timezone


# Create your models here.
class ProductType(models.Model):
    product_type = models.CharField(max_length=150)

    class Meta:
        db_table = "product_type"


class Product(models.Model):
    product_name = models.CharField(max_length=150)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING)
    stock_amount = models.IntegerField()
    price = models.FloatField()
    promotion = models.FloatField(blank=True)

    class Meta:
        db_table = "product"


class User(models.Model):
    user_name = models.CharField(max_length=30)
    created_at = models.DateTimeField()

    class Meta:
        db_table = "user"


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    basket_status = models.CharField(max_length=30)
    created_time = models.DateTimeField()
    expiry_time = models.DateTimeField()

    def is_expired(self):
        if timezone.now() > self.expiry_time:
            return True
        return False

    class Meta:
        db_table = "basket"


class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        db_table = "basket_item"
