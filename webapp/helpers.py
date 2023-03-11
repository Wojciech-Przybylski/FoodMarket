from datetime import datetime, timedelta

from django.core.exceptions import ObjectDoesNotExist

from webapp.models import User, Basket


def get_current_user(user_email):
    return User.objects.get(user_email=user_email)


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
        print("Basket does not exist for user: " + current_user.user_email)
        return create_new_basket(current_user)


def create_new_basket(current_user):
    return Basket.objects.create(user=current_user, basket_status="created", created_time=datetime.now(),
                                 expiry_time=datetime.now() + timedelta(minutes=10))