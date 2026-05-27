from django.urls import re_path, path
from django.http import JsonResponse
from .views import home_view

def dummy_devtools(request):
    return JsonResponse({})  # Renvoie un JSON vide pour éviter le 404

urlpatterns = [
    re_path(r'^\.well-known/appspecific/com\.chrome\.devtools\.json$', dummy_devtools),
    path('', home_view, name='home'),  # Exemple d'autre URL
]
