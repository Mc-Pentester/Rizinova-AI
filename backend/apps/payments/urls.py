from django.urls import path
from .views import CreatePaymentAPIView

urlpatterns = [
    path("create/", CreatePaymentAPIView.as_view(), name="payment-create"),
]
