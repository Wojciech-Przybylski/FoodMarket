from django.db import models


# Create your models here.
class ProductType(models.Model):
    product_type_id = models.BigAutoField(primary_key=True)
    product_type = models.CharField(max_length=150)

    class Meta:
        db_table = "product_type"


class Product(models.Model):
    product_id = models.BigAutoField(primary_key=True)
    product_name = models.CharField(max_length=150)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING)
    stock_amount = models.IntegerField()
    price = models.FloatField()
    promotion = models.FloatField(blank=True)

    class Meta:
        db_table = "product"


class Basket(models.Model):
    basket_id = models.BigAutoField(primary_key=True)
    basket_status = models.CharField(max_length=150)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = "basket"


class BasketItem(models.Model):
    basket_item_id = models.BigAutoField(primary_key=True)
    basket_id = models.ForeignKey(Basket, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()

    class Meta:
        db_table = "basket_item"



