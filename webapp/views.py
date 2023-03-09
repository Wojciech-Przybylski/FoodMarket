from django.shortcuts import render
from webapp.models import Product
# Create your views here.


def index(request):
    products = Product.objects.all()
    return render(request, "index.html", {"products": products})


