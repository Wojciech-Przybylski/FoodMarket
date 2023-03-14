from datetime import datetime, timedelta

from django.db.models import Sum, Case, When, F, FloatField

from webapp.models import User, Basket, BasketItem, Product, Order


class BasketManager:
    def get_user_basket(self, user):
        try:
            basket = Basket.objects.get(user=user, basket_status="created")
            if basket.is_expired():
                basket.basket_status = "expired"
                basket.save()
            else:
                return basket
        except Basket.DoesNotExist:
            print(f"Basket does not exist for user: {user.user_email}")
            return self.__create_new_basket(user)

    def get_basket_total_quantity(self, user):
        return BasketItem.objects.filter(basket=self.get_user_basket(user)).aggregate(Sum("quantity"))["quantity__sum"]

    def get_basket_total_price(self, user):
        return self.get_basket_totals(user).aggregate(total_price=Sum('total_product_price'))['total_price']

    def get_basket_totals(self, user):
        return BasketItem.objects.filter(basket=self.get_user_basket(user)).values('product__product_name') \
            .annotate(
            total_product_quantity=Sum('quantity'),
            product__price=Case(When(product__promotion__isnull=False, then=F('product__promotion')),
                                default=F('product__price'), output_field=FloatField()),
            total_product_price=F('quantity') * F('product__price'))

    def create_order(self, basket, total_price):
        Order.objects.create(basket=basket, total_price=total_price, created_at=datetime.now())

        basket.basket_status = "completed"
        basket.save()

    def create_basket_item(self, product_id, basket, quantity_input):
        BasketItem.objects.create(product=Product.objects.get(id=product_id), quantity=quantity_input, basket=basket)
        basket.expiry_time = datetime.now() + timedelta(minutes=10)
        basket.save()

    def update_stock_quantity(self, basket):
        for item in BasketItem.objects.filter(basket=basket):
            item.product.stock_amount -= item.quantity
            item.product.save()

    def __create_new_basket(self, user):
        return Basket.objects.create(user=user, basket_status="created", created_time=datetime.now(),
                                     expiry_time=datetime.now() + timedelta(minutes=10))


class UserManager:

    def __init__(self):
        self.user_email = None

    def create_user(self, user_email, encoded_password):
        return User.objects.create(user_email=user_email, user_password=encoded_password, created_at=datetime.now())

    def get_current_user(self):
        return User.objects.get(user_email=self.user_email)

    def set_user_email(self, user_email):
        self.user_email = user_email


class OrderDTO:

    def __init__(self, order_date, order_total_price, items):
        self.order_date = order_date
        self.order_total_price = order_total_price
        self.items = items

    def __str__(self):
        return f"OrderDTO[{self.order_date}, {self.order_total_price}, {self.items}]"
