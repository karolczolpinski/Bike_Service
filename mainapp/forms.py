from django import forms
from django.contrib.auth.models import User

from .models import (
    Rower,
    Zgloszenie,
    Uzytkownik,
    Czesc,
    Diagnoza,
    RaportNaprawy,
    ZuzytaCzesc,
    ZamowienieCzesci,
)

class RowerForm(forms.ModelForm):
    class Meta:
        model = Rower
        fields = ['klient', 'marka', 'model', 'typ', 'numer_seryjny']
        labels = {
            'klient': 'Klient',
            'marka': 'Marka',
            'model': 'Model',
            'typ': 'Typ roweru',
            'numer_seryjny': 'Numer seryjny',
        }


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

    def clean_login(self):
        login = self.cleaned_data['login']

        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('Konto logowania o takim loginie już istnieje.')

        if Uzytkownik.objects.filter(login=login).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim loginie już istnieje.')

        return login

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Konto logowania o takim adresie email już istnieje.')

        if Uzytkownik.objects.filter(email=email).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim adresie email już istnieje.')

        return email
        
class RejestracjaKlientaForm(forms.Form):
    imie = forms.CharField(label='Imię', max_length=50)
    nazwisko = forms.CharField(label='Nazwisko', max_length=50)
    email = forms.EmailField(label='Email', max_length=100)
    login = forms.CharField(label='Login', max_length=50)
    haslo = forms.CharField(label='Hasło', widget=forms.PasswordInput)
    powtorz_haslo = forms.CharField(label='Powtórz hasło', widget=forms.PasswordInput)

    def clean_login(self):
        login = self.cleaned_data['login']

        if User.objects.filter(username=login).exists():
            raise forms.ValidationError('Konto o takim loginie już istnieje.')

        if Uzytkownik.objects.filter(login=login).exists():
            raise forms.ValidationError('Użytkownik aplikacji o takim loginie już istnieje.')

        return login

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