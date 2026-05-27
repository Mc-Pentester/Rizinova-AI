from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from apps.conversations.views import chat_page, compte

# Endpoint dummy pour Chrome DevTools
def dummy_devtools(request):
    return JsonResponse({})  # Renvoie un JSON vide

urlpatterns = [
    # Toujours en premier pour attraper la requête avant les autres
    re_path(r'^\.well-known/appspecific/com\.chrome\.devtools\.json$', dummy_devtools),


    path("admin/", admin.site.urls),

    # Pages WEB (templates)
    path("", include("apps.conversations.web_urls")),

    # API
    path("api/users/", include("apps.users.urls")),
    path("chat/", chat_page, name="chat-page"),
    path("compte/", compte, name="compte"),
    path('', include("apps.core.urls")),
    path("api/chat/", include("apps.conversations.urls")),
    path("api/knowledge/", include("apps.knowledge.urls")),
    path("api/payments/", include("apps.payments.urls")),
    path("api/subscriptions/", include("apps.subscriptions.urls")),
]
