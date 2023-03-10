from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('basket', views.basket_page, name='basket'),
    path('stock/<id>/addItem', views.add_item, name='add_item')
]
