from django.db.models import Sum, F, Case, When, FloatField
from django.shortcuts import render, redirect
from django.views import View

from webapp.helpers import get_current_user, get_user_basket
from webapp.models import Product, BasketItem


class IndexView(View):
    def get(self, request):
        products = Product.objects.all()
        user = get_current_user()
        basket = get_user_basket(user)
        basket_total_quantity = BasketItem.objects.filter(basket=basket).aggregate(Sum("quantity"))["quantity__sum"]

        context = {"products": products, "basket": basket, "basket_total_quantity": basket_total_quantity}

        return render(request, "index.html", context)


class BasketPageView(View):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.basket = get_user_basket(get_current_user())
        self.basket_total_quantity = BasketItem.objects.filter(basket=self.basket).aggregate(Sum("quantity"))[
            "quantity__sum"]

        self.basket_totals = BasketItem.objects.filter(basket_id=self.basket).values('product__product_name')\
            .annotate(
                total_product_quantity=Sum('quantity'),
                product__price=Case(When(product__promotion__isnull=False, then=F('product__promotion')), default=F('product__price'), output_field=FloatField()),
                total_product_price=F('quantity') * F('product__price')
        )

        self.total_price = self.basket_totals.aggregate(total_price=Sum('total_product_price'))['total_price']

    def get(self, request):
        context = {"basket_view": self}
        return render(request, "basket.html", context)

    def post(self, request, id):
        user = get_current_user()
        basket = get_user_basket(user)

        BasketItem.objects.create(product=Product.objects.get(id=id),
                                  quantity=request.POST.get("quantity_input"), basket=basket)

        return redirect('index')
