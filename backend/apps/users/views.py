from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class RegisterAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username et password requis"}, status=400)
        
        from django.contrib.auth.models import User
        if User.objects.filter(username=username).exists():
            return Response({"error": "Utilisateur existe déjà"}, status=400)

        User.objects.create_user(username=username, password=password)
        return Response({"message": "Compte créé avec succès"})

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)  # Active la session pour l'utilisateur
            return Response({
                "message": "Connexion réussie",
                "plan": getattr(user.profile, "plan", "free")
            })
        return Response({"error": "Identifiants invalides"}, status=401)

class LogoutAPIView(APIView):
    def post(self, request):
        logout(request)
        return Response({"message": "Déconnecté avec succès"})
