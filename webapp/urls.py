from django.urls import path
from . import views

urlpatterns = [
    path('', views.LoginPageView.as_view(), name='login'),
    path('register', views.RegisterPageView.as_view(), name='register'),
    path('home', views.HomeView.as_view(), name='home'),
    path('basket', views.BasketPageView.as_view(), name='basket'),
    path('addItem/<id>', views.BasketPageView.as_view(), name='addItem'),
    path('basket', views.BasketPageView.as_view(), name='check_out'),

]
