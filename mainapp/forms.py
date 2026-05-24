from django import forms
from django.contrib.auth.models import User

from .models import Rower, Zgloszenie, Uzytkownik

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