from django.contrib import admin
from .models import (
    Uzytkownik,
    Rower,
    Zgloszenie,
    ZlecenieSerwisowe,
    Diagnoza,
    RaportNaprawy,
    Czesc,
    ZuzytaCzesc,
    Powiadomienie,
    Magazyn,
    Platnosc,
    Adres,
    Kontakt,
    ProducentRoweru,
    TypRoweru,
    KategoriaCzesci,
    Dostawca,
    ZamowienieCzesci,
    PozycjaZamowienia,
    HistoriaStatusu,
    TerminSerwisu,
    StanowiskoSerwisowe,
    UslugaSerwisowa,
    WykonanaUsluga,
    NotatkaSerwisowa,
)


@admin.register(Uzytkownik)
class UzytkownikAdmin(admin.ModelAdmin):
    list_display = ('imie', 'nazwisko', 'email', 'login', 'rola')
    list_filter = ('rola',)
    search_fields = ('imie', 'nazwisko', 'email', 'login')
    readonly_fields = ('haslo',)


@admin.register(Rower)
class RowerAdmin(admin.ModelAdmin):
    list_display = ('marka', 'model', 'typ', 'klient')
    search_fields = ('marka', 'model', 'numer_seryjny')
    list_filter = ('typ',)


@admin.register(Zgloszenie)
class ZgloszenieAdmin(admin.ModelAdmin):
    list_display = ('klient', 'rower', 'data_zgloszenia', 'status')
    list_filter = ('status', 'data_zgloszenia')
    search_fields = ('opis_usterki',)


@admin.register(ZlecenieSerwisowe)
class ZlecenieSerwisoweAdmin(admin.ModelAdmin):
    list_display = ('zgloszenie', 'mechanik', 'data_przyjecia', 'data_zakonczenia', 'status')
    list_filter = ('status', 'data_przyjecia')
    search_fields = ('status',)


@admin.register(Diagnoza)
class DiagnozaAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'data_diagnozy')
    search_fields = ('opis_diagnozy',)


@admin.register(RaportNaprawy)
class RaportNaprawyAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'data_raportu')
    search_fields = ('opis_czynnosci',)


@admin.register(Czesc)
class CzescAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'kategoria', 'stan_magazynowy', 'stan_minimalny', 'cena')
    list_filter = ('kategoria',)
    search_fields = ('nazwa',)


@admin.register(ZuzytaCzesc)
class ZuzytaCzescAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'czesc', 'ilosc')
    list_filter = ('czesc',)


@admin.register(Powiadomienie)
class PowiadomienieAdmin(admin.ModelAdmin):
    list_display = ('uzytkownik', 'zlecenie', 'data_wyslania')
    list_filter = ('data_wyslania',)
    search_fields = ('tresc',)

@admin.register(Magazyn)
class MagazynAdmin(admin.ModelAdmin):
    list_display = ('czesc', 'ilosc', 'typ_operacji', 'data_operacji')
    list_filter = ('typ_operacji', 'data_operacji')


@admin.register(Platnosc)
class PlatnoscAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'kwota', 'data_platnosci', 'status', 'metoda_platnosci')
    list_filter = ('status', 'metoda_platnosci')


@admin.register(Adres)
class AdresAdmin(admin.ModelAdmin):
    list_display = ('uzytkownik', 'ulica', 'numer_budynku', 'kod_pocztowy', 'miasto')
    search_fields = ('ulica', 'miasto', 'kod_pocztowy')


@admin.register(Kontakt)
class KontaktAdmin(admin.ModelAdmin):
    list_display = ('uzytkownik', 'telefon', 'dodatkowy_email', 'preferowany_kontakt')
    list_filter = ('preferowany_kontakt',)
    search_fields = ('telefon', 'dodatkowy_email')


@admin.register(ProducentRoweru)
class ProducentRoweruAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'kraj', 'strona_www')
    search_fields = ('nazwa', 'kraj')


@admin.register(TypRoweru)
class TypRoweruAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')
    search_fields = ('nazwa',)


@admin.register(KategoriaCzesci)
class KategoriaCzesciAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'opis')
    search_fields = ('nazwa',)


@admin.register(Dostawca)
class DostawcaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'nip', 'email', 'telefon')
    search_fields = ('nazwa', 'nip', 'email', 'telefon')


@admin.register(ZamowienieCzesci)
class ZamowienieCzesciAdmin(admin.ModelAdmin):
    list_display = ('dostawca', 'data_zamowienia', 'status')
    list_filter = ('status', 'data_zamowienia')
    search_fields = ('uwagi',)


@admin.register(PozycjaZamowienia)
class PozycjaZamowieniaAdmin(admin.ModelAdmin):
    list_display = ('zamowienie', 'czesc', 'ilosc', 'cena_jednostkowa')
    list_filter = ('czesc',)


@admin.register(HistoriaStatusu)
class HistoriaStatusuAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'status', 'data_zmiany')
    list_filter = ('status', 'data_zmiany')
    search_fields = ('komentarz',)


@admin.register(TerminSerwisu)
class TerminSerwisuAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'stanowisko', 'data_terminu')
    list_filter = ('stanowisko', 'data_terminu')


@admin.register(StanowiskoSerwisowe)
class StanowiskoSerwisoweAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'czy_aktywne')
    list_filter = ('czy_aktywne',)
    search_fields = ('nazwa',)


@admin.register(UslugaSerwisowa)
class UslugaSerwisowaAdmin(admin.ModelAdmin):
    list_display = ('nazwa', 'cena', 'czas_szacowany_minuty')
    search_fields = ('nazwa',)


@admin.register(WykonanaUsluga)
class WykonanaUslugaAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'usluga', 'ilosc', 'cena_wykonania')
    list_filter = ('usluga',)


@admin.register(NotatkaSerwisowa)
class NotatkaSerwisowaAdmin(admin.ModelAdmin):
    list_display = ('zlecenie', 'autor', 'data_dodania')
    list_filter = ('data_dodania',)
    search_fields = ('tresc',)