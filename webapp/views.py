from datetime import datetime

from django.contrib.auth.hashers import PBKDF2PasswordHasher
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.views import View

from webapp.helpers import UserManager, BasketManager, OrderDTO
from webapp.models import Product, BasketItem, User, Order, Basket

user_mgr = UserManager()
basket_mgr = BasketManager()


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
                    user_mgr.set_user_email(current_user.user_email)
                    return redirect("home")
                else:
                    return redirect("login")
            except ObjectDoesNotExist:
                return render(request, LoginPageView.template, {"login_failed": True})
        elif "register" in request.POST:
            return redirect("register")

#TODO when registered set current user as registered

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
            current_user = user_mgr.create_user(user_email, encoded_password)
            request.session['current_user_email'] = current_user.user_email
            user_mgr.set_user_email(current_user.user_email)
        except Exception as e:
            print("Something bad happened, couldn't create new user: ", e)

        return redirect("home")


class HomeView(View):
    template = "home.html"
    url = "/home"

    def get(self, request):
        current_user_email = request.session.get('current_user_email', None)

        products = Product.objects.all()
        user = user_mgr.get_current_user()
        basket = basket_mgr.get_user_basket(user)
        basket_total_quantity = basket_mgr.get_basket_total_quantity(user)

        context = {"products": products,
                   "basket": basket,
                   "basket_total_quantity": basket_total_quantity,
                   "current_user_email": current_user_email}

        return render(request, self.template, context)


class OrderView(View):
    template_name = "orders.html"
    url = "/orders"

    def get(self, request):
        user = user_mgr.get_current_user()
        baskets = Basket.objects.filter(user=user, basket_status='completed')

        order_dtos = []
        for basket in baskets:
            order = Order.objects.filter(basket=basket).first()

            if order:
                order_items = BasketItem.objects.filter(basket=basket)
                order_dto = OrderDTO(order.created_at, order.total_price, order_items)
                order_dtos.append(order_dto)

        context = {"order_dtos": order_dtos,
                   "current_user_email": user.user_email}

        return render(request, self.template_name, context)


class BasketPageView(View):
    template = "basket.html"
    url = "/basket"

    def get(self, request):
        user = user_mgr.get_current_user()

        basket_total_quantity = basket_mgr.get_basket_total_quantity(user)
        basket_totals = basket_mgr.get_basket_totals(user)

        context = {"basket_totals": basket_totals,
                   "basket_total_quantity": basket_total_quantity,
                   "current_user_email": user.user_email}
        return render(request, self.template, context)

    def post(self, request, id=None):
        user = user_mgr.get_current_user()
        basket = basket_mgr.get_user_basket(user)

        if "add_item" in request.POST:
            quantity_input = request.POST.get("quantity_input")

            if quantity_input == "0":
                return redirect('home')
            else:
                basket_mgr.create_basket_item(id, basket, quantity_input)
                basket_mgr.update_stock_quantity(basket)

        if "check_out" in request.POST:

            total_price = basket_mgr.get_basket_total_price(user)
            basket_mgr.create_order(basket, total_price)

        return redirect('home')
