from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import RegisterViewset, LoginViewset, google_login

from .views import google_login
router = DefaultRouter()
router.register('register', RegisterViewset, basename='register')
router.register('login', LoginViewset, basename='login')
urlpatterns = router.urls
urlpatterns += [
    path('api/google-login/', google_login, name='google_login'),
]