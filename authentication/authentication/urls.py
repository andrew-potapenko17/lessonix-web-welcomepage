from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name="main"),
    path('login/', views.login, name="login"),
    path('register/', views.register, name="register"),
    path('admin/', admin.site.urls),
]
