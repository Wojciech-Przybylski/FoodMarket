from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Q, F
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from webapp.models import Product, Basket, User, BasketItem
from datetime import datetime, timedelta


# Create your views here.

def index(request):
    products = Product.objects.all()
    user = get_current_user()
    basket = get_user_basket(user)
    basket_total_quantity = BasketItem.objects.filter(basket=basket).aggregate(Sum("quantity"))["quantity__sum"]
    return render(request, "index.html",
                  {"products": products, "basket": basket, "basket_total_quantity": basket_total_quantity})


class BasketView:
    def __init__(self, basket):
        self.basket_total_quantity = BasketItem.objects.filter(basket=basket).aggregate(Sum("quantity"))[
            "quantity__sum"]

        self.basket_totals = BasketItem.objects.filter(basket_id=basket).values(
            'product__product_name', 'product__price'
        ).annotate(
            total_product_quantity=Sum('quantity'),
            total_product_price=Sum(F('quantity') * F('product__price'))
        ).order_by(
            'product__product_name'
        )

        self.total_price = self.basket_totals.aggregate(
            total_price=Sum('total_product_price')
        )['total_price']


def basket_page(request):
    user = get_current_user()
    basket_view = BasketView(basket=get_user_basket(user))
    return render(request, "basket.html", {"basket_view": basket_view})


def add_item(request, id):
    user = get_current_user()
    basket = get_user_basket(user)

    BasketItem.objects.create(product=Product.objects.get(id=id), quantity=request.POST.get("quantity_input"),
                              basket=basket)

    return HttpResponseRedirect(reverse(index))


def get_current_user():
    return User.objects.get(id=1)


def get_user_basket(current_user):
    try:
        basket = Basket.objects.get(user=current_user, basket_status="created")
        if basket.is_expired():
            basket.basket_status = "expired"
            basket.save()
            return create_new_basket(current_user)
        else:
            return basket
    except ObjectDoesNotExist:
        print("Basket does not exist for user: " + current_user.user_name)
        return create_new_basket(current_user)


def create_new_basket(current_user):
    return Basket.objects.create(user=current_user, basket_status="created", created_time=datetime.now(),
                                 expiry_time=datetime.now() + timedelta(minutes=5))
