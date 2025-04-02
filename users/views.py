from django.shortcuts import render
from rest_framework import viewsets, permissions 
from .serializers import * 
from .models import * 
from rest_framework.response import Response 
from django.contrib.auth import get_user_model, authenticate
from knox.models import AuthToken
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests
import json

User = get_user_model()

class LoginViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer

    def create(self, request): 
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(): 
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            user = authenticate(request, email=email, password=password)
            if user: 
                _, token = AuthToken.objects.create(user)
                return Response(
                    {
                        "user": self.serializer_class(user).data,
                        "token": token
                    }
                )
            else: 
                return Response({"error":"Invalid credentials"}, status=401)    
        else: 
            return Response(serializer.errors,status=400)



class RegisterViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else: 
            return Response(serializer.errors,status=400)


def google_login(request):
    data = json.loads(request.body)
    token = data.get('token')

    print("Received token:", token)  # DEBUG

    try:
        idinfo = id_token.verify_oauth2_token(
            token, requests.Request(), 
            "480903099299-1fud6itlcocakhlatehb6mdeuidknm0k.apps.googleusercontent.com"
        )
        email = idinfo.get("email")

        # Vérification utilisateur
        user, created = User.objects.get_or_create(email=email, defaults={"username": email})
        
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(user)

        return JsonResponse({"token": str(refresh.access_token), "user": {"email": user.email}})
    
    except Exception as e:
        print("Google Auth Error:", e)  # DEBUG
        return JsonResponse({"error": "Failed to authenticate with Google"}, status=400)
