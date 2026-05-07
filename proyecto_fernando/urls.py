"""
URL configuration for proyecto_fernando project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from proyectos_academicos import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticación - Requisitos 1.1, 1.2
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Dashboard - Requisito 1.3
    path('dashboard/', app_views.dashboard_redirect, name='dashboard'),
]

# Servir archivos media en desarrollo - Requisito 16.6
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
