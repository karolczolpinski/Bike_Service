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
    
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    
    path('panel-klienta/', views.panel_klienta, name='panel_klienta'),
    path('panel-mechanika/', views.panel_mechanika, name='panel_mechanika'),
    path('panel-magazyniera/', views.panel_magazyniera, name='panel_magazyniera'),

    path('zlecenia/', views.zlecenia, name='zlecenia'),
    path('zlecenia/przyjmij/<int:zlecenie_id>/', views.przyjmij_zlecenie, name='przyjmij_zlecenie'),

    path('diagnozy/dodaj/', views.dodaj_diagnoze, name='dodaj_diagnoze'),
    path('raporty/dodaj/', views.dodaj_raport, name='dodaj_raport'),
    path('zuzyte-czesci/dodaj/', views.dodaj_zuzyta_czesc, name='dodaj_zuzyta_czesc'),

    path('czesci/dodaj/', views.dodaj_czesc, name='dodaj_czesc'),

    path('zamowienia-czesci/', views.zamowienia_czesci, name='zamowienia_czesci'),
    path('zamowienia-czesci/dodaj/', views.dodaj_zamowienie_czesci, name='dodaj_zamowienie_czesci'),
]