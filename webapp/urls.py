from django.urls import path
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('basket', views.BasketPageView.as_view(), name='basket'),
    path('stock/<id>/addItem', views.BasketPageView.as_view(), name='add_item')
]
