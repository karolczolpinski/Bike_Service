from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render

from django.contrib.auth import login
from django.db import transaction

from .forms import RowerForm, ZgloszenieForm, UzytkownikCreateForm, RejestracjaKlientaForm
from .models import Czesc, Rower, Uzytkownik, Zgloszenie


def pobierz_uzytkownika_aplikacji(request):
    """
    Łączy użytkownika Django z użytkownikiem aplikacji MAINAPP.
    Warunek: auth.User.username musi być taki sam jak Uzytkownik.login.
    """
    if not request.user.is_authenticated:
        return None

    return Uzytkownik.objects.filter(login=request.user.username).first()


def czy_ma_role(request, dozwolone_role):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        return False

    return uzytkownik.rola in dozwolone_role


def home(request):
    context = {
        'liczba_uzytkownikow': Uzytkownik.objects.count(),
        'liczba_rowerow': Rower.objects.count(),
        'liczba_zgloszen': Zgloszenie.objects.count(),
        'liczba_czesci': Czesc.objects.count(),
        'uzytkownik_aplikacji': pobierz_uzytkownika_aplikacji(request),
    }

    return render(request, 'home.html', context)

def rejestracja(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RejestracjaKlientaForm(request.POST)

        if form.is_valid():
            imie = form.cleaned_data['imie']
            nazwisko = form.cleaned_data['nazwisko']
            email = form.cleaned_data['email']
            login_uzytkownika = form.cleaned_data['login']
            haslo = form.cleaned_data['haslo']

            with transaction.atomic():
                konto = User.objects.create_user(
                    username=login_uzytkownika,
                    password=haslo,
                    email=email,
                    first_name=imie,
                    last_name=nazwisko,
                )

                Uzytkownik.objects.create(
                    imie=imie,
                    nazwisko=nazwisko,
                    email=email,
                    login=login_uzytkownika,
                    haslo=haslo,
                    rola='klient',
                )

            login(request, konto)
            messages.success(request, 'Konto klienta zostało utworzone. Zostałeś zalogowany.')
            return redirect('home')
    else:
        form = RejestracjaKlientaForm()

    return render(request, 'rejestracja.html', {'form': form})

@login_required
def panel_admin(request):
    if not czy_ma_role(request, ['admin']):
        messages.error(request, 'Nie masz uprawnień do panelu administratora aplikacji.')
        return redirect('home')

    context = {
        'liczba_uzytkownikow': Uzytkownik.objects.count(),
        'liczba_rowerow': Rower.objects.count(),
        'liczba_zgloszen': Zgloszenie.objects.count(),
        'liczba_czesci': Czesc.objects.count(),
        'uzytkownicy': Uzytkownik.objects.all().order_by('nazwisko', 'imie'),
        'ostatnie_zgloszenia': Zgloszenie.objects.all().order_by('-data_zgloszenia')[:5],
    }

    return render(request, 'panel_admin.html', context)

@login_required
def dodaj_uzytkownika(request):
    if not czy_ma_role(request, ['admin']):
        messages.error(request, 'Nie masz uprawnień do dodawania użytkowników.')
        return redirect('home')

    if request.method == 'POST':
        form = UzytkownikCreateForm(request.POST)

        if form.is_valid():
            imie = form.cleaned_data['imie']
            nazwisko = form.cleaned_data['nazwisko']
            email = form.cleaned_data['email']
            login = form.cleaned_data['login']
            haslo = form.cleaned_data['haslo']
            rola = form.cleaned_data['rola']

            User.objects.create_user(
                username=login,
                password=haslo,
                email=email,
                first_name=imie,
                last_name=nazwisko,
            )

            Uzytkownik.objects.create(
                imie=imie,
                nazwisko=nazwisko,
                email=email,
                login=login,
                haslo=haslo,
                rola=rola,
            )

            messages.success(request, 'Użytkownik został utworzony.')
            return redirect('panel_admin')
    else:
        form = UzytkownikCreateForm()

    return render(request, 'dodaj_uzytkownika.html', {'form': form})

@login_required
def rowery(request):
    rowery = Rower.objects.all()
    return render(request, 'rowery.html', {'rowery': rowery})


@login_required
def zgloszenia(request):
    zgloszenia = Zgloszenie.objects.all()
    return render(request, 'zgloszenia.html', {'zgloszenia': zgloszenia})


@login_required
def czesci(request):
    czesci = Czesc.objects.all()
    return render(request, 'czesci.html', {'czesci': czesci})


@login_required
def dodaj_rower(request):
    if not czy_ma_role(request, ['klient', 'admin']):
        messages.error(request, 'Nie masz uprawnień do dodawania roweru.')
        return redirect('home')

    if request.method == 'POST':
        form = RowerForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('rowery')
    else:
        form = RowerForm()

    return render(request, 'dodaj_rower.html', {'form': form})


@login_required
def dodaj_zgloszenie(request):
    if not czy_ma_role(request, ['klient', 'admin']):
        messages.error(request, 'Nie masz uprawnień do dodawania zgłoszenia.')
        return redirect('home')

    if request.method == 'POST':
        form = ZgloszenieForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('zgloszenia')
    else:
        form = ZgloszenieForm()

    return render(request, 'dodaj_zgloszenie.html', {'form': form})