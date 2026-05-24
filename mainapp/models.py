from django.db import models


class Uzytkownik(models.Model):
    ROLE_CHOICES = [
        ('klient', 'Klient'),
        ('mechanik', 'Mechanik'),
        ('magazynier', 'Magazynier'),
        ('admin', 'Admin'),
    ]

    imie = models.CharField(max_length=50)
    nazwisko = models.CharField(max_length=50)
    email = models.EmailField(max_length=100, unique=True)
    login = models.CharField(max_length=50, unique=True)
    haslo = models.CharField(max_length=255)
    rola = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        verbose_name = 'Użytkownik'
        verbose_name_plural = 'Użytkownicy'

    def __str__(self):
        return f'{self.imie} {self.nazwisko}'


class Rower(models.Model):
    klient = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='rowery')
    producent = models.ForeignKey(
        'ProducentRoweru',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rowery'
    )
    typ_roweru = models.ForeignKey(
        'TypRoweru',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='rowery'
    )
    marka = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    typ = models.CharField(max_length=50)
    numer_seryjny = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Rower"
        verbose_name_plural = "Rowery"

    def __str__(self):
        return f"{self.marka} {self.model}"


class Zgloszenie(models.Model):
    STATUS_CHOICES = [
        ('nowe', 'Nowe'),
        ('w_trakcie', 'W trakcie'),
        ('zakonczone', 'Zakończone'),
    ]

    klient = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='zgloszenia')
    rower = models.ForeignKey(Rower, on_delete=models.CASCADE, related_name='zgloszenia')
    data_zgloszenia = models.DateTimeField(auto_now_add=True)
    opis_usterki = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='nowe')

    class Meta:
        verbose_name = 'Zgłoszenie'
        verbose_name_plural = 'Zgłoszenia'

    def __str__(self):
        return f'Zgłoszenie #{self.id}'


class ZlecenieSerwisowe(models.Model):
    STATUS_CHOICES = [
        ('przyjete', 'Przyjęte'),
        ('diagnoza', 'Diagnoza'),
        ('naprawa', 'Naprawa'),
        ('gotowe', 'Gotowe'),
    ]

    zgloszenie = models.ForeignKey(Zgloszenie, on_delete=models.CASCADE, related_name='zlecenia')
    mechanik = models.ForeignKey(Uzytkownik, on_delete=models.SET_NULL, null=True, blank=True, related_name='zlecenia_mechanika')
    data_przyjecia = models.DateTimeField(auto_now_add=True)
    data_zakonczenia = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='przyjete')

    class Meta:
        verbose_name = 'Zlecenie serwisowe'
        verbose_name_plural = 'Zlecenia serwisowe'

    def __str__(self):
        return f'Zlecenie #{self.id}'


class Diagnoza(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='diagnozy')
    opis_diagnozy = models.TextField()
    data_diagnozy = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Diagnoza"
        verbose_name_plural = "Diagnozy"
    
    def __str__(self):
        return f'Diagnoza #{self.id}'


class RaportNaprawy(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='raporty')
    opis_czynnosci = models.TextField()
    data_raportu = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Raport naprawy"
        verbose_name_plural = "Raporty napraw"
        
    def __str__(self):
        return f'Raport #{self.id}'


class Czesc(models.Model):
    kategoria = models.ForeignKey(
        'KategoriaCzesci',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='czesci'
    )
    nazwa = models.CharField(max_length=100)
    stan_magazynowy = models.IntegerField()
    stan_minimalny = models.IntegerField()
    cena = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Część"
        verbose_name_plural = "Części"

    def __str__(self):
        return self.nazwa
        

class ZuzytaCzesc(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='zuzyte_czesci')
    czesc = models.ForeignKey(Czesc, on_delete=models.CASCADE, related_name='zuzycia')
    ilosc = models.IntegerField(default=1)
    
    class Meta:
        verbose_name = "Zużyta część"
        verbose_name_plural = "Zużyte części"

    def __str__(self):
        return f'{self.czesc} x {self.ilosc}'


class Powiadomienie(models.Model):
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='powiadomienia')
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='powiadomienia')
    tresc = models.TextField()
    data_wyslania = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Powiadomienie"
        verbose_name_plural = "Powiadomienia"

    def __str__(self):
        return f'Powiadomienie #{self.id}'


class Magazyn(models.Model):
    TYP_CHOICES = [
        ('przyjecie', 'Przyjęcie'),
        ('wydanie', 'Wydanie'),
    ]

    czesc = models.ForeignKey(Czesc, on_delete=models.CASCADE, related_name='operacje_magazynowe')
    ilosc = models.IntegerField()
    typ_operacji = models.CharField(max_length=20, choices=TYP_CHOICES)
    data_operacji = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Operacja magazynowa"
        verbose_name_plural = "Magazyn"
        
    def __str__(self):
        return f'{self.typ_operacji} - {self.czesc}'


class Platnosc(models.Model):
    STATUS_CHOICES = [
        ('oczekuje', 'Oczekuje'),
        ('oplacona', 'Opłacona'),
        ('anulowana', 'Anulowana'),
    ]

    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='platnosci')
    kwota = models.DecimalField(max_digits=10, decimal_places=2)
    data_platnosci = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='oczekuje')
    metoda_platnosci = models.CharField(max_length=30, default='gotowka')

    class Meta:
        verbose_name = "Płatność"
        verbose_name_plural = "Płatności"

    def __str__(self):
        return f"Płatność #{self.id} - {self.kwota} zł"
        

class Adres(models.Model):
    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='adresy')
    ulica = models.CharField(max_length=100)
    numer_budynku = models.CharField(max_length=10)
    numer_lokalu = models.CharField(max_length=10, blank=True)
    kod_pocztowy = models.CharField(max_length=10)
    miasto = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Adres"
        verbose_name_plural = "Adresy"

    def __str__(self):
        return f"{self.ulica} {self.numer_budynku}, {self.miasto}"


class Kontakt(models.Model):
    PREFEROWANY_KONTAKT = [
        ('telefon', 'Telefon'),
        ('email', 'E-mail'),
    ]

    uzytkownik = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='kontakty')
    telefon = models.CharField(max_length=20)
    dodatkowy_email = models.EmailField(max_length=100, blank=True)
    preferowany_kontakt = models.CharField(
        max_length=20,
        choices=PREFEROWANY_KONTAKT,
        default='telefon'
    )

    class Meta:
        verbose_name = "Kontakt"
        verbose_name_plural = "Kontakty"

    def __str__(self):
        return f"{self.uzytkownik} - {self.telefon}"
        
class ProducentRoweru(models.Model):
    nazwa = models.CharField(max_length=100)
    kraj = models.CharField(max_length=50, blank=True)
    strona_www = models.URLField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Producent roweru"
        verbose_name_plural = "Producenci rowerów"

    def __str__(self):
        return self.nazwa
        
class TypRoweru(models.Model):
    nazwa = models.CharField(max_length=50)
    opis = models.TextField(blank=True)

    class Meta:
        verbose_name = "Typ roweru"
        verbose_name_plural = "Typy rowerów"

    def __str__(self):
        return self.nazwa
        
class KategoriaCzesci(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)

    class Meta:
        verbose_name = "Kategoria części"
        verbose_name_plural = "Kategorie części"

    def __str__(self):
        return self.nazwa
        
class Dostawca(models.Model):
    nazwa = models.CharField(max_length=100)
    nip = models.CharField(max_length=20, blank=True)
    email = models.EmailField(max_length=100, blank=True)
    telefon = models.CharField(max_length=20, blank=True)
    adres = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Dostawca"
        verbose_name_plural = "Dostawcy"

    def __str__(self):
        return self.nazwa
        
class ZamowienieCzesci(models.Model):
    STATUS_CHOICES = [
        ('nowe', 'Nowe'),
        ('zamowione', 'Zamówione'),
        ('dostarczone', 'Dostarczone'),
        ('anulowane', 'Anulowane'),
    ]

    dostawca = models.ForeignKey(Dostawca, on_delete=models.CASCADE, related_name='zamowienia')
    data_zamowienia = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='nowe')
    uwagi = models.TextField(blank=True)

    class Meta:
        verbose_name = "Zamówienie części"
        verbose_name_plural = "Zamówienia części"

    def __str__(self):
        return f"Zamówienie #{self.id} - {self.dostawca}"
        
class PozycjaZamowienia(models.Model):
    zamowienie = models.ForeignKey(ZamowienieCzesci, on_delete=models.CASCADE, related_name='pozycje')
    czesc = models.ForeignKey(Czesc, on_delete=models.CASCADE, related_name='pozycje_zamowien')
    ilosc = models.PositiveIntegerField()
    cena_jednostkowa = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Pozycja zamówienia"
        verbose_name_plural = "Pozycje zamówień"

    def __str__(self):
        return f"{self.czesc} x {self.ilosc}"
        
class HistoriaStatusu(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='historia_statusow')
    status = models.CharField(max_length=30)
    data_zmiany = models.DateTimeField(auto_now_add=True)
    komentarz = models.TextField(blank=True)

    class Meta:
        verbose_name = "Historia statusu"
        verbose_name_plural = "Historie statusów"

    def __str__(self):
        return f"{self.zlecenie} - {self.status}"
        
class StanowiskoSerwisowe(models.Model):
    nazwa = models.CharField(max_length=50)
    opis = models.TextField(blank=True)
    czy_aktywne = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Stanowisko serwisowe"
        verbose_name_plural = "Stanowiska serwisowe"

    def __str__(self):
        return self.nazwa
        
class TerminSerwisu(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='terminy')
    stanowisko = models.ForeignKey(
        StanowiskoSerwisowe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='terminy'
    )
    data_terminu = models.DateTimeField()
    opis = models.TextField(blank=True)

    class Meta:
        verbose_name = "Termin serwisu"
        verbose_name_plural = "Terminy serwisu"

    def __str__(self):
        return f"Termin #{self.id} - {self.data_terminu}"
        

class UslugaSerwisowa(models.Model):
    nazwa = models.CharField(max_length=100)
    opis = models.TextField(blank=True)
    cena = models.DecimalField(max_digits=10, decimal_places=2)
    czas_szacowany_minuty = models.PositiveIntegerField(default=30)

    class Meta:
        verbose_name = "Usługa serwisowa"
        verbose_name_plural = "Usługi serwisowe"

    def __str__(self):
        return self.nazwa
        
class WykonanaUsluga(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='wykonane_uslugi')
    usluga = models.ForeignKey(UslugaSerwisowa, on_delete=models.CASCADE, related_name='wykonania')
    ilosc = models.PositiveIntegerField(default=1)
    cena_wykonania = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = "Wykonana usługa"
        verbose_name_plural = "Wykonane usługi"

    def __str__(self):
        return f"{self.usluga} - {self.zlecenie}"
        
class NotatkaSerwisowa(models.Model):
    zlecenie = models.ForeignKey(ZlecenieSerwisowe, on_delete=models.CASCADE, related_name='notatki')
    autor = models.ForeignKey(Uzytkownik, on_delete=models.CASCADE, related_name='notatki_serwisowe')
    tresc = models.TextField()
    data_dodania = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notatka serwisowa"
        verbose_name_plural = "Notatki serwisowe"

    def __str__(self):
        return f"Notatka #{self.id} - {self.zlecenie}"
        
