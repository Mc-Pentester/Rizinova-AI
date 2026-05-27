from django.urls import path
from .views import chat_page, compte

urlpatterns = [
    path("chat/", chat_page, name="chat-page"),
    path("compte/", compte, name="compte"),
]
