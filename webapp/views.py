from datetime import datetime, timedelta

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, F, Case, When, FloatField
from django.shortcuts import render, redirect
from django.views import View

from webapp.helpers import get_current_user, get_user_basket
from webapp.models import Product, BasketItem, User, Order, Basket


class LoginPageView(View):
    template = "login.html"
    url = ""

    def get(self, request):
        return render(request, self.template)

    def post(self, request):

        if "login" in request.POST:
            user_email = request.POST.get('email')
            user_password = request.POST.get('password')

            try:
                current_user = User.objects.get(user_email=user_email)

                if PBKDF2PasswordHasher().verify(user_password, current_user.user_password):
                    request.session['current_user_email'] = current_user.user_email
                    return redirect("home")
                else:
                    return redirect("login")
            except ObjectDoesNotExist:
                return render(request, LoginPageView.template, {"login_failed": True})
        elif "register" in request.POST:
            return redirect("register")


class RegisterPageView(View):
    template = "register.html"
    url = "/register"

    def get(self, request):
        return render(request, self.template)

    def post(self, request):
        user_email = request.POST.get('email')
        user_password = request.POST.get('password')

        encoded_password = PBKDF2PasswordHasher().encode(password=user_password, salt=PBKDF2PasswordHasher().salt())

        try:
            current_user = User.objects.create(user_email=user_email, user_password=encoded_password,
                                               created_at=datetime.now())
            request.session['current_user_email'] = current_user.user_email
        except Exception as e:
            print("Something bad happened: ", e)

        return redirect("home")


class HomeView(View):
    template = "home.html"
    url = "/home"

    def get(self, request):
        current_user_email = request.session.get('current_user_email', None)

        products = Product.objects.all()
        user = get_current_user(current_user_email)
        basket = get_user_basket(user)
        basket_total_quantity = BasketItem.objects.filter(basket=basket).aggregate(Sum("quantity"))["quantity__sum"]

        context = {"products": products, "basket": basket, "basket_total_quantity": basket_total_quantity,
                   "current_user_email": current_user_email}

        return render(request, self.template, context)


class OrderView(View):
    template_name = "orders.html"
    url = "/orders"

    def get(self, request):
        current_user_email = request.session.get('current_user_email')
        user = get_current_user(current_user_email)
        baskets = Basket.objects.filter(user=user, basket_status='completed')

        order_dtos = []
        for basket in baskets:
            order = Order.objects.filter(basket=basket).first()

            if order:
                order_items = BasketItem.objects.filter(basket=basket)
                order_dto = OrderDTO(order.created_at, order.total_price, order_items)
                order_dtos.append(order_dto)

        context = {"order_dtos": order_dtos, "current_user_email": current_user_email}
        return render(request, self.template_name, context)


class OrderDTO:

    def __init__(self, order_date, order_total_price, items):
        self.order_date = order_date
        self.order_total_price = order_total_price
        self.items = items

    def __str__(self):
        return f"OrderDTO[{self.order_date}, {self.order_total_price}, {self.items}]"


class BasketPageView(View):
    template = "basket.html"
    url = "/basket"

    def init(self, current_user_email):
        self.basket = get_user_basket(get_current_user(current_user_email))
        self.basket_total_quantity = BasketItem.objects.filter(basket=self.basket).aggregate(Sum("quantity"))[
            "quantity__sum"]

        self.basket_totals = BasketItem.objects.filter(basket_id=self.basket).values('product__product_name') \
            .annotate(
            total_product_quantity=Sum('quantity'),
            product__price=Case(When(product__promotion__isnull=False, then=F('product__promotion')),
                                default=F('product__price'), output_field=FloatField()),
            total_product_price=F('quantity') * F('product__price')
        )

        self.total_price = self.basket_totals.aggregate(total_price=Sum('total_product_price'))['total_price']

    def get(self, request):
        current_user_email = request.session.get('current_user_email', None)

        self.init(current_user_email)

        basket_total_quantity = BasketItem.objects.filter(basket=self.basket).aggregate(Sum("quantity"))[
            "quantity__sum"]

        context = {"basket_view": self, "current_user_email": current_user_email,
                   "basket_total_quantity": basket_total_quantity}
        return render(request, self.template, context)

    def post(self, request, id=None):
        current_user_email = request.session.get('current_user_email', None)

        user = get_current_user(current_user_email)
        basket = get_user_basket(user)

        if request.method == "POST" and "add_item" in request.POST:
            quantity_input = request.POST.get("quantity_input")
            if quantity_input == "0":
                return redirect('home')
            else:
                BasketItem.objects.create(product=Product.objects.get(id=id), quantity=quantity_input, basket=basket)

                basket.expiry_time = datetime.now() + timedelta(minutes=10)
                basket.save()

        if request.method == "POST" and "check_out" in request.POST:
            basket_items = BasketItem.objects.filter(basket=basket)
            # Update product stock for each basket item
            for item in basket_items:
                item.product.stock_amount -= item.quantity
                item.product.save()

            basket_totals = BasketItem.objects.filter(basket_id=basket).values('product__product_name') \
                .annotate(
                total_product_quantity=Sum('quantity'),
                product__price=Case(When(product__promotion__isnull=False, then=F('product__promotion')),
                                    default=F('product__price'), output_field=FloatField()),
                total_product_price=F('quantity') * F('product__price')
            )
            total_price = basket_totals.aggregate(total_price=Sum('total_product_price'))['total_price']
            Order.objects.create(basket=basket, total_price=total_price, created_at=datetime.now())

            basket.basket_status = "completed"
            basket.save()

        return redirect('home')
