from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('panel-admin/', views.panel_admin, name='panel_admin'),

    path('rowery/', views.rowery, name='rowery'),
    path('rowery/dodaj/', views.dodaj_rower, name='dodaj_rower'),

    path('zgloszenia/', views.zgloszenia, name='zgloszenia'),
    path('zgloszenia/dodaj/', views.dodaj_zgloszenie, name='dodaj_zgloszenie'),

    path('czesci/', views.czesci, name='czesci'),
    
    path('panel-admin/uzytkownicy/dodaj/', views.dodaj_uzytkownika, name='dodaj_uzytkownika'),
]