from datetime import datetime, timedelta

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, F, Case, When, FloatField
from django.shortcuts import render, redirect
from django.views import View

from webapp.helpers import get_current_user, get_user_basket
from webapp.models import Product, BasketItem, User


class LoginPageView(View):
    template = "login.html"
    url = ""

    def get(self, request):
        return render(request, self.template)

    def post(self, request):

        if request.method == "POST" and "login" in request.POST:
            user_email = request.POST.get('email')
            user_password = request.POST.get('password')

            try:
                current_user = User.objects.get(user_email=user_email)

                if PBKDF2PasswordHasher().verify(user_password, current_user.user_password):
                    print("password matching, logging in")
                    request.session['current_user_email'] = current_user.user_email
                    return redirect("home")
                else:
                    print("login failed")
                    return redirect("login")
            except ObjectDoesNotExist:
                print("user does not exist, needs to register")
                return render(request, LoginPageView.template, {"login_failed": True})
        if request.method == "POST" and "register" in request.POST:
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

        return render(request, "home.html", context)


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

        context = {"basket_view": self, "current_user_email": current_user_email}
        return render(request, self.template, context)

    def post(self, request, id):
        current_user_email = request.session.get('current_user_email', None)

        user = get_current_user(current_user_email)
        basket = get_user_basket(user)

        quantity_input = request.POST.get("quantity_input")

        BasketItem.objects.create(product=Product.objects.get(id=id), quantity=quantity_input, basket=basket)

        basket.expiry_time = datetime.now() + timedelta(minutes=10)
        basket.save()

        return redirect('home')
