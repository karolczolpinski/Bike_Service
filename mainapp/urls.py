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
    path('rowery/<int:rower_id>/edytuj/', views.edytuj_rower, name='edytuj_rower'),
    path('rowery/<int:rower_id>/', views.szczegoly_roweru, name='szczegoly_roweru'),

    path('zgloszenia/', views.zgloszenia, name='zgloszenia'),
    path('zgloszenia/dodaj/', views.dodaj_zgloszenie, name='dodaj_zgloszenie'),
    path('zgloszenia/<int:zgloszenie_id>/edytuj/', views.edytuj_zgloszenie, name='edytuj_zgloszenie'),
    path('zgloszenia/<int:zgloszenie_id>/', views.szczegoly_zgloszenia, name='szczegoly_zgloszenia'),

    path('czesci/', views.czesci, name='czesci'),
    path('czesci/dodaj/', views.dodaj_czesc, name='dodaj_czesc'),
    path('czesci/<int:czesc_id>/', views.szczegoly_czesci, name='szczegoly_czesci'),
    path('czesci/<int:czesc_id>/edytuj/', views.edytuj_czesc, name='edytuj_czesc'),
    
    path('panel-admin/uzytkownicy/dodaj/', views.dodaj_uzytkownika, name='dodaj_uzytkownika'),
    
    path('rejestracja/', views.rejestracja, name='rejestracja'),
    
    path('panel-klienta/', views.panel_klienta, name='panel_klienta'),
    path('panel-mechanika/', views.panel_mechanika, name='panel_mechanika'),
    path('panel-magazyniera/', views.panel_magazyniera, name='panel_magazyniera'),

    path('zlecenia/', views.zlecenia, name='zlecenia'),
    path('zlecenia/przyjmij/<int:zlecenie_id>/', views.przyjmij_zlecenie, name='przyjmij_zlecenie'),
    path('zlecenia/<int:zlecenie_id>/', views.szczegoly_zlecenia, name='szczegoly_zlecenia'),
    path('zlecenia/<int:zlecenie_id>/status/', views.zmien_status, name='zmien_status'),

    path('zamowienia-czesci/', views.zamowienia_czesci, name='zamowienia_czesci'),
    path('zamowienia-czesci/dodaj/', views.dodaj_zamowienie_czesci, name='dodaj_zamowienie_czesci'),
    path('pozycje-zamowienia/dodaj/', views.dodaj_pozycje_zamowienia, name='dodaj_pozycje_zamowienia'),
    path('zamowienia-czesci/<int:zamowienie_id>/', views.szczegoly_zamowienia_czesci, name='szczegoly_zamowienia_czesci'),
    path('zamowienia-czesci/<int:zamowienie_id>/usun/', views.usun_zamowienie_czesci, name='usun_zamowienie_czesci'),
    
    path('powiadomienia/', views.powiadomienia, name='powiadomienia'),
    
    path('platnosci/', views.platnosci, name='platnosci'),
    path('platnosci/dodaj/', views.dodaj_platnosc, name='dodaj_platnosc'),
    
    
    
    path('moje-dane/', views.moje_dane, name='moje_dane'),
    path('moje-dane/adres/', views.edytuj_adres, name='edytuj_adres'),
    path('moje-dane/kontakt/', views.edytuj_kontakt, name='edytuj_kontakt'),
    
    path('zlecenia/<int:zlecenie_id>/notatka/dodaj/', views.dodaj_notatke_serwisowa, name='dodaj_notatke_serwisowa'),
    path('zlecenia/<int:zlecenie_id>/termin/dodaj/', views.dodaj_termin_serwisu, name='dodaj_termin_serwisu'),
    path('zlecenia/<int:zlecenie_id>/usluga/dodaj/', views.dodaj_wykonana_usluga, name='dodaj_wykonana_usluga'),
    path('zlecenia/<int:zlecenie_id>/edytuj/', views.edytuj_zlecenie, name='edytuj_zlecenie'),
    path('zlecenia/<int:zlecenie_id>/anuluj/', views.anuluj_zlecenie, name='anuluj_zlecenie'),
    
    path('diagnozy/', views.diagnozy, name='diagnozy'),
    path('raporty/', views.raporty, name='raporty'),
    path('zuzyte-czesci/', views.zuzyte_czesci, name='zuzyte_czesci'),
    
    path('diagnozy/dodaj/', views.dodaj_diagnoze, name='dodaj_diagnoze'),
    path('raporty/dodaj/', views.dodaj_raport, name='dodaj_raport'),
    path('zuzyte-czesci/dodaj/', views.dodaj_zuzyta_czesc, name='dodaj_zuzyta_czesc'),
    
    path('zlecenia/', views.zlecenia, name='zlecenia'),
    path('zlecenia/<int:zlecenie_id>/', views.szczegoly_zlecenia, name='szczegoly_zlecenia'),
    path('zlecenia/<int:zlecenie_id>/status/', views.zmien_status, name='zmien_status'),
    path('zlecenia/<int:zlecenie_id>/przyjmij/', views.przyjmij_zlecenie, name='przyjmij_zlecenie'),
    
    path('dostawcy/', views.dostawcy, name='dostawcy'),
    path('dostawcy/dodaj/', views.dodaj_dostawce, name='dodaj_dostawce'),
    path('magazyn/', views.magazyn, name='magazyn'),
    path('magazyn/operacja/dodaj/', views.dodaj_operacje_magazynowa, name='dodaj_operacje_magazynowa'),
    
    path('panel-admin/uzytkownicy/', views.uzytkownicy_aplikacji, name='uzytkownicy_aplikacji'),
    path('panel-admin/uzytkownicy/<int:uzytkownik_id>/', views.szczegoly_uzytkownika, name='szczegoly_uzytkownika'),
    path('panel-admin/uzytkownicy/<int:uzytkownik_id>/edytuj/', views.edytuj_uzytkownika_aplikacji, name='edytuj_uzytkownika_aplikacji'),
    
    path('platnosci/', views.platnosci, name='platnosci'),
    path('platnosci/dodaj/', views.dodaj_platnosc, name='dodaj_platnosc'),
    path('platnosci/<int:platnosc_id>/', views.szczegoly_platnosci, name='szczegoly_platnosci'),
    path('platnosci/<int:platnosc_id>/edytuj/', views.edytuj_platnosc, name='edytuj_platnosc'),
    
    path('uzytkownicy/<int:uzytkownik_id>/dezaktywuj/', views.dezaktywuj_uzytkownika, name='dezaktywuj_uzytkownika'),
]