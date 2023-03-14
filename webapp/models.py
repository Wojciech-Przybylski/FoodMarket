from django.db import models
from django.utils import timezone


# Create your models here.
class ProductType(models.Model):
    product_type = models.CharField(max_length=150)

    def __str__(self):
        return f"ProductType[{self.product_type}]"

    class Meta:
        db_table = "product_type"


class Product(models.Model):
    product_name = models.CharField(max_length=150)
    product_type = models.ForeignKey(ProductType, on_delete=models.DO_NOTHING)
    stock_amount = models.IntegerField()
    price = models.FloatField()
    promotion = models.FloatField(blank=True)

    def get_price(self):
        if self.promotion is not None:
            return self.promotion
        return self.price

    def __str__(self):
        return f"Product[{self.product_name}, {self.product_type}, {self.stock_amount}, {self.price}, {self.promotion}]"

    class Meta:
        db_table = "product"


class User(models.Model):
    user_email = models.CharField(max_length=50)
    user_password = models.CharField(max_length=128)
    created_at = models.DateTimeField()

    def __str__(self):
        return f"User[{self.user_email}, {self.user_password}, {self.created_at}]"

    class Meta:
        db_table = "user"


class Basket(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    basket_status = models.CharField(max_length=30)
    created_time = models.DateTimeField()
    expiry_time = models.DateTimeField()

    def __str__(self):
        return f"Basket[{self.user}, {self.basket_status}, {self.created_time}, {self.expiry_time}]"

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

    def __str__(self):
        return f"BasketItem[{self.basket}, {self.product}, {self.quantity}]"

    class Meta:
        db_table = "basket_item"


class Order(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.DO_NOTHING)
    total_price = models.FloatField()
    created_at = models.DateTimeField()

    def __str__(self):
        return f"Order[{self.basket}, {self.total_price}, {self.created_at}]"

    class Meta:
        db_table = "order"
