from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('social-auth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
]
