from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('stock/<id>/addItem', views.add_item, name='add_item')
]
