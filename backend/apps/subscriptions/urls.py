from django.urls import path
from .views import SubscriptionStatusAPIView

urlpatterns = [
    path("status/", SubscriptionStatusAPIView.as_view(), name="subscription-status"),
]
