from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('social-auth/', include('social_django.urls', namespace='social')),  # Handles the OAuth2 flow
    path('complete/google-oauth2/', views.google_auth_success, name="google_auth_success"),
    path('complete/facebook/', views.facebook_auth_success, name="facebook_auth_success"),
    path('complete/twitter/', views.twitter_auth_success, name="twitter_auth_success"),
    path('privacypolicy/student', views.privacypolicy, name='privacypolicy'),
    path('admin/', admin.site.urls),
]
