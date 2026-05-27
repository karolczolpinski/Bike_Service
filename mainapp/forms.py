from django import forms
from django.contrib.auth.models import User
import re

from .models import (
    Rower,
    Zgloszenie,
    Uzytkownik,
    Czesc,
    Diagnoza,
    RaportNaprawy,
    ZuzytaCzesc,
    ZamowienieCzesci,
    Platnosc,
    PozycjaZamowienia,
    ZlecenieSerwisowe,
    Adres,
    Kontakt,
    NotatkaSerwisowa,
    TerminSerwisu,
    WykonanaUsluga,
    Dostawca,
    Magazyn,
)

POLISH_NAME_PATTERN = re.compile(r'^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż\-\s]+$')

def validate_person_name(value, field_label):
    value = value.strip()

    if len(value) < 2:
        raise forms.ValidationError(f'{field_label} musi mieć co najmniej 2 znaki.')

    if not POLISH_NAME_PATTERN.match(value):
        raise forms.ValidationError(
            f'{field_label} może zawierać tylko litery, spacje i myślniki.'
        )

    return value


def validate_login(value):
    value = value.strip()

    if len(value) < 3:
        raise forms.ValidationError('Login musi mieć co najmniej 3 znaki.')

    if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
        raise forms.ValidationError(
            'Login może zawierać tylko litery, cyfry, kropkę, myślnik i podkreślenie.'
        )

    return value.lower()

class RowerForm(forms.ModelForm):
    class Meta:
        model = Rower
        fields = [
            'klient',
            'producent',
            'typ_roweru',
            'model',
            'numer_seryjny',
        ]
        labels = {
            'klient': 'Klient',
            'producent': 'Producent',
            'typ_roweru': 'Typ roweru',
            'model': 'Model',
            'numer_seryjny': 'Numer seryjny',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['producent'].required = True
        self.fields['typ_roweru'].required = True

    def clean_model(self):
        model = self.cleaned_data.get('model', '').strip()

        if len(model) < 2:
            raise forms.ValidationError('Model roweru musi mieć co najmniej 2 znaki.')

        return model

    def clean_numer_seryjny(self):
        numer = self.cleaned_data.get('numer_seryjny', '').strip()

        if len(numer) < 5:
            raise forms.ValidationError('Numer seryjny musi mieć co najmniej 5 znaków.')

        return numer.upper()

class ZgloszenieForm(forms.ModelForm):
    class Meta:
        model = Zgloszenie
        fields = ['klient', 'rower', 'opis_usterki', 'status']
        labels = {
            'klient': 'Klient',
            'rower': 'Rower',
            'opis_usterki': 'Opis usterki',
            'status': 'Status',
        }
    
class UzytkownikCreateForm(forms.Form):
    ROLE_CHOICES = [
        ('klient', 'Klient'),
        ('mechanik', 'Mechanik'),
        ('magazynier', 'Magazynier'),
        ('admin', 'Admin'),
    ]

    imie = forms.CharField(label='Imię', max_length=50)
    nazwisko = forms.CharField(label='Nazwisko', max_length=50)
    email = forms.EmailField(label='Email', max_length=100)
    login = forms.CharField(label='Login', max_length=50)
    haslo = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    rola = forms.ChoiceField(label='Rola', choices=ROLE_CHOICES)

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Konto logowania o takim adresie email już istnieje.')

        if Uzytkownik.objects.filter(email=email).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim adresie email już istnieje.')

        return email
        
    def clean_imie(self):
        return validate_person_name(self.cleaned_data.get('imie', ''), 'Imię')

    def clean_nazwisko(self):
        return validate_person_name(self.cleaned_data.get('nazwisko', ''), 'Nazwisko')

    def clean_login(self):
        login = validate_login(self.cleaned_data.get('login', ''))

        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('Użytkownik o takim loginie już istnieje.')

        if Uzytkownik.objects.filter(login=login).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim loginie już istnieje.')

        return login

    def clean_haslo(self):
        haslo = self.cleaned_data.get('haslo', '')

        if len(haslo) < 8:
            raise forms.ValidationError('Hasło musi mieć co najmniej 8 znaków.')

        if not any(char.isdigit() for char in haslo):
            raise forms.ValidationError('Hasło musi zawierać co najmniej jedną cyfrę.')

        if not any(char.isupper() for char in haslo):
            raise forms.ValidationError('Hasło musi zawierać co najmniej jedną wielką literę.')

        return haslo
        
class RejestracjaKlientaForm(forms.Form):
    imie = forms.CharField(label='Imię', max_length=50)
    nazwisko = forms.CharField(label='Nazwisko', max_length=50)
    email = forms.EmailField(label='Email', max_length=100)
    login = forms.CharField(label='Login', max_length=50)
    haslo = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    powtorz_haslo = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Konto o takim adresie email już istnieje.')

        if Uzytkownik.objects.filter(email=email).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim adresie email już istnieje.')

        return email

    def clean(self):
        cleaned_data = super().clean()
        haslo = cleaned_data.get('haslo')
        powtorz_haslo = cleaned_data.get('powtorz_haslo')

        if haslo and powtorz_haslo and haslo != powtorz_haslo:
            raise forms.ValidationError('Podane hasła nie są takie same.')

        return cleaned_data
        
    def clean_imie(self):
        return validate_person_name(self.cleaned_data.get('imie', ''), 'Imię')

    def clean_nazwisko(self):
        return validate_person_name(self.cleaned_data.get('nazwisko', ''), 'Nazwisko')

    def clean_login(self):
        login = validate_login(self.cleaned_data.get('login', ''))

        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('Użytkownik o takim loginie już istnieje.')

        if Uzytkownik.objects.filter(login=login).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim loginie już istnieje.')

        return login

    def clean_haslo(self):
        haslo = self.cleaned_data.get('haslo', '')

        if len(haslo) < 8:
            raise forms.ValidationError('Hasło musi mieć co najmniej 8 znaków.')

        if not any(char.isdigit() for char in haslo):
            raise forms.ValidationError('Hasło musi zawierać co najmniej jedną cyfrę.')

        if not any(char.isupper() for char in haslo):
            raise forms.ValidationError('Hasło musi zawierać co najmniej jedną wielką literę.')

        return haslo
        
class CzescForm(forms.ModelForm):
    class Meta:
        model = Czesc
        fields = ['kategoria', 'nazwa', 'stan_magazynowy', 'stan_minimalny', 'cena']
        labels = {
            'kategoria': 'Kategoria',
            'nazwa': 'Nazwa części',
            'stan_magazynowy': 'Stan magazynowy',
            'stan_minimalny': 'Stan minimalny',
            'cena': 'Cena',
        }


class DiagnozaForm(forms.ModelForm):
    class Meta:
        model = Diagnoza
        fields = ['zlecenie', 'opis_diagnozy']
        labels = {
            'zlecenie': 'Zlecenie serwisowe',
            'opis_diagnozy': 'Opis diagnozy',
        }


class RaportNaprawyForm(forms.ModelForm):
    class Meta:
        model = RaportNaprawy
        fields = ['zlecenie', 'opis_czynnosci']
        labels = {
            'zlecenie': 'Zlecenie serwisowe',
            'opis_czynnosci': 'Opis wykonanych czynności',
        }


class ZuzytaCzescForm(forms.ModelForm):
    class Meta:
        model = ZuzytaCzesc
        fields = ['zlecenie', 'czesc', 'ilosc']
        labels = {
            'zlecenie': 'Zlecenie serwisowe',
            'czesc': 'Część',
            'ilosc': 'Ilość',
        }


class ZamowienieCzesciForm(forms.ModelForm):
    class Meta:
        model = ZamowienieCzesci
        fields = ['dostawca', 'status', 'uwagi']
        labels = {
            'dostawca': 'Dostawca',
            'status': 'Status',
            'uwagi': 'Uwagi',
        }
        
class PlatnoscForm(forms.ModelForm):
    class Meta:
        model = Platnosc
        fields = ['zlecenie', 'kwota', 'data_platnosci', 'status', 'metoda_platnosci']
        labels = {
            'zlecenie': 'Zlecenie',
            'kwota': 'Kwota',
            'data_platnosci': 'Data płatności',
            'status': 'Status',
            'metoda_platnosci': 'Metoda płatności',
        }
        
class PozycjaZamowieniaForm(forms.ModelForm):
    class Meta:
        model = PozycjaZamowienia
        fields = ['zamowienie', 'czesc', 'ilosc', 'cena_jednostkowa']
        labels = {
            'zamowienie': 'Zamówienie',
            'czesc': 'Część',
            'ilosc': 'Ilość',
            'cena_jednostkowa': 'Cena jednostkowa',
        }
        
class StatusZleceniaForm(forms.ModelForm):
    komentarz = forms.CharField(
        label='Komentarz do zmiany statusu',
        widget=forms.Textarea,
        required=False
    )

    class Meta:
        model = ZlecenieSerwisowe
        fields = ['status']
        labels = {
            'status': 'Nowy status',
        }
    
class AdresForm(forms.ModelForm):
    class Meta:
        model = Adres
        fields = [
            'ulica',
            'numer_budynku',
            'numer_lokalu',
            'kod_pocztowy',
            'miasto',
        ]
        labels = {
            'ulica': 'Ulica',
            'numer_budynku': 'Numer budynku',
            'numer_lokalu': 'Numer lokalu',
            'kod_pocztowy': 'Kod pocztowy',
            'miasto': 'Miasto',
        }

    def clean_ulica(self):
        ulica = self.cleaned_data.get('ulica', '').strip()

        if len(ulica) < 2:
            raise forms.ValidationError('Ulica musi mieć co najmniej 2 znaki.')

        return ulica

    def clean_miasto(self):
        miasto = self.cleaned_data.get('miasto', '').strip()

        if len(miasto) < 2:
            raise forms.ValidationError('Miasto musi mieć co najmniej 2 znaki.')

        return miasto

class KontaktForm(forms.ModelForm):
    class Meta:
        model = Kontakt
        fields = [
            'telefon',
            'dodatkowy_email',
            'preferowany_kontakt',
        ]
        labels = {
            'telefon': 'Telefon',
            'dodatkowy_email': 'Dodatkowy email',
            'preferowany_kontakt': 'Preferowany kontakt',
        }

    def clean_telefon(self):
        telefon = self.cleaned_data.get('telefon', '').strip()

        if len(telefon) < 7:
            raise forms.ValidationError('Numer telefonu musi mieć co najmniej 7 znaków.')

        return telefon
        
class NotatkaSerwisowaForm(forms.ModelForm):
    class Meta:
        model = NotatkaSerwisowa
        fields = ['tresc']
        labels = {
            'tresc': 'Treść notatki',
        }


class TerminSerwisuForm(forms.ModelForm):
    class Meta:
        model = TerminSerwisu
        fields = ['stanowisko', 'data_terminu', 'opis']
        labels = {
            'stanowisko': 'Stanowisko',
            'data_terminu': 'Data terminu',
            'opis': 'Opis',
        }


class WykonanaUslugaForm(forms.ModelForm):
    class Meta:
        model = WykonanaUsluga
        fields = ['usluga', 'ilosc', 'cena_wykonania']
        labels = {
            'usluga': 'Usługa',
            'ilosc': 'Ilość',
            'cena_wykonania': 'Cena wykonania',
        }

    def clean_ilosc(self):
        ilosc = self.cleaned_data.get('ilosc')

        if ilosc <= 0:
            raise forms.ValidationError('Ilość musi być większa od zera.')

        return ilosc

class DostawcaForm(forms.ModelForm):
    class Meta:
        model = Dostawca
        fields = ['nazwa', 'nip', 'email', 'telefon', 'adres']


class OperacjaMagazynowaForm(forms.ModelForm):
    class Meta:
        model = Magazyn
        fields = ['czesc', 'ilosc', 'typ_operacji']
        labels = {
            'czesc': 'Część',
            'ilosc': 'Ilość',
            'typ_operacji': 'Typ operacji',
        }

    def clean_ilosc(self):
        ilosc = self.cleaned_data.get('ilosc')

        if ilosc <= 0:
            raise forms.ValidationError('Ilość musi być większa od zera.')

        return ilosc
        
class UzytkownikProfilForm(forms.ModelForm):
    class Meta:
        model = Uzytkownik
        fields = ['imie', 'nazwisko', 'email', 'rola']
        labels = {
            'imie': 'Imię',
            'nazwisko': 'Nazwisko',
            'email': 'Email',
            'rola': 'Rola',
        }

    def clean_imie(self):
        return validate_person_name(self.cleaned_data.get('imie', ''), 'Imię')

    def clean_nazwisko(self):
        return validate_person_name(self.cleaned_data.get('nazwisko', ''), 'Nazwisko')