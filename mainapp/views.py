from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404

from django.contrib.auth import login
from django.db import transaction

from django.db.models import F

from .forms import (
    RowerForm,
    ZgloszenieForm,
    UzytkownikCreateForm,
    RejestracjaKlientaForm,
    CzescForm,
    DiagnozaForm,
    RaportNaprawyForm,
    ZuzytaCzescForm,
    ZamowienieCzesciForm,
    PlatnoscForm,
    PozycjaZamowieniaForm,
    StatusZleceniaForm,
)
from .models import (
    Czesc,
    Diagnoza,
    RaportNaprawy,
    Rower,
    Uzytkownik,
    Zgloszenie,
    ZlecenieSerwisowe,
    ZuzytaCzesc,
    ZamowienieCzesci,
    ZlecenieSerwisowe,
    Powiadomienie,
    HistoriaStatusu,
    Platnosc,
    PozycjaZamowienia,
)

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

def wymagaj_roli(request, dozwolone_role, komunikat='Brak uprawnień.'):
    if not czy_ma_role(request, dozwolone_role):
        messages.error(request, komunikat)
        return False

    return True
    
def zmien_status_zlecenia(zlecenie, nowy_status, komentarz):
    zlecenie.status = nowy_status
    zlecenie.save()

    HistoriaStatusu.objects.create(
        zlecenie=zlecenie,
        status=nowy_status,
        komentarz=komentarz
    )

    Powiadomienie.objects.create(
        uzytkownik=zlecenie.zgloszenie.klient,
        zlecenie=zlecenie,
        tresc=komentarz
    )

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
                    haslo='Hasło przechowywane w Django Auth',
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
                haslo='Hasło przechowywane w Django Auth',
                rola=rola,
            )

            messages.success(request, 'Użytkownik został utworzony.')
            return redirect('panel_admin')
    else:
        form = UzytkownikCreateForm()

    return render(request, 'dodaj_uzytkownika.html', {'form': form})

@login_required
def rowery(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'klient':
        rowery = Rower.objects.filter(klient=uzytkownik)
    else:
        rowery = Rower.objects.all()

    return render(request, 'rowery.html', {'rowery': rowery})


@login_required
def zgloszenia(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'klient':
        zgloszenia = Zgloszenie.objects.filter(klient=uzytkownik)
    else:
        zgloszenia = Zgloszenie.objects.all()

    return render(request, 'zgloszenia.html', {'zgloszenia': zgloszenia})

@login_required
def czesci(request):
    if not wymagaj_roli(request, ['mechanik', 'magazynier', 'admin'], 'Brak dostępu do magazynu części.'):
        return redirect('home')

    czesci = Czesc.objects.all()
    return render(request, 'czesci.html', {'czesci': czesci})

@login_required
def dodaj_rower(request):
    if not wymagaj_roli(request, ['klient', 'admin'], 'Tylko klient lub admin może dodać rower.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if request.method == 'POST':
        form = RowerForm(request.POST)

        if uzytkownik.rola == 'klient':
            form.fields['klient'].required = False

        if form.is_valid():
            rower = form.save(commit=False)

            if uzytkownik.rola == 'klient':
                rower.klient = uzytkownik
                
            rower.marka = rower.producent.nazwa
            rower.typ = rower.typ_roweru.nazwa

            rower.save()
            messages.success(request, 'Rower został dodany.')
            return redirect('rowery')
    else:
        form = RowerForm()

        if uzytkownik.rola == 'klient':
            form.fields['klient'].initial = uzytkownik
            form.fields['klient'].disabled = True

    return render(request, 'dodaj_rower.html', {'form': form})
    
@login_required
def dodaj_zgloszenie(request):
    if not wymagaj_roli(request, ['klient', 'admin'], 'Tylko klient lub admin może dodać zgłoszenie.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if request.method == 'POST':
        form = ZgloszenieForm(request.POST)

        if uzytkownik.rola == 'klient':
            form.fields['klient'].required = False
            form.fields['status'].required = False
            form.fields['rower'].queryset = Rower.objects.filter(klient=uzytkownik)

        if form.is_valid():
            zgloszenie = form.save(commit=False)

            if uzytkownik.rola == 'klient':
                zgloszenie.klient = uzytkownik
                zgloszenie.status = 'nowe'

            zgloszenie.save()

            mechanik = Uzytkownik.objects.filter(rola='mechanik').first()

            if mechanik:
                zlecenie = ZlecenieSerwisowe.objects.create(
                    zgloszenie=zgloszenie,
                    mechanik=mechanik,
                    status='nowe'
                )

                HistoriaStatusu.objects.create(
                    zlecenie=zlecenie,
                    status='nowe',
                    komentarz='Zlecenie zostało automatycznie utworzone po dodaniu zgłoszenia.'
                )

                Powiadomienie.objects.create(
                    uzytkownik=zgloszenie.klient,
                    zlecenie=zlecenie,
                    tresc='Twoje zgłoszenie zostało przyjęte. Utworzono zlecenie serwisowe.'
                )

                messages.success(request, 'Zgłoszenie zostało dodane i utworzono zlecenie serwisowe.')
            else:
                messages.warning(
                    request,
                    'Zgłoszenie zostało dodane, ale nie utworzono zlecenia, ponieważ nie ma mechanika w systemie.'
                )

            return redirect('zgloszenia')
    else:
        form = ZgloszenieForm()

        if uzytkownik.rola == 'klient':
            form.fields['klient'].initial = uzytkownik
            form.fields['klient'].disabled = True

            form.fields['status'].initial = 'nowe'
            form.fields['status'].disabled = True

            form.fields['rower'].queryset = Rower.objects.filter(klient=uzytkownik)

    return render(request, 'dodaj_zgloszenie.html', {'form': form})
        
@login_required
def panel_klienta(request):
    if not wymagaj_roli(request, ['klient', 'admin'], 'Dostęp tylko dla klienta.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik.rola == 'admin':
        rowery = Rower.objects.all()
        zgloszenia = Zgloszenie.objects.all()
    else:
        rowery = Rower.objects.filter(klient=uzytkownik)
        zgloszenia = Zgloszenie.objects.filter(klient=uzytkownik)

    context = {
        'rowery': rowery,
        'zgloszenia': zgloszenia,
        'liczba_rowerow': rowery.count(),
        'liczba_zgloszen': zgloszenia.count(),
    }

    return render(request, 'panel_klienta.html', context)


@login_required
def panel_mechanika(request):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Dostęp tylko dla mechanika.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik.rola == 'admin':
        zlecenia = ZlecenieSerwisowe.objects.all()
    else:
        zlecenia = ZlecenieSerwisowe.objects.filter(mechanik=uzytkownik)

    context = {
        'zlecenia': zlecenia,
        'liczba_zlecen': zlecenia.count(),
        'zgloszenia_nowe': Zgloszenie.objects.filter(status='nowe'),
    }

    return render(request, 'panel_mechanika.html', context)


@login_required
def panel_magazyniera(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Dostęp tylko dla magazyniera.'):
        return redirect('home')

    context = {
        'czesci': Czesc.objects.all(),
        'zamowienia': ZamowienieCzesci.objects.all().order_by('-data_zamowienia')[:10],
        'liczba_czesci': Czesc.objects.count(),
        'czesci_niski_stan': Czesc.objects.filter(stan_magazynowy__lte=F('stan_minimalny')),
    }

    return render(request, 'panel_magazyniera.html', context)
    
@login_required
def zlecenia(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'klient':
        zlecenia = ZlecenieSerwisowe.objects.filter(zgloszenie__klient=uzytkownik)
    elif uzytkownik.rola == 'mechanik':
        zlecenia = ZlecenieSerwisowe.objects.filter(mechanik=uzytkownik)
    elif uzytkownik.rola == 'admin':
        zlecenia = ZlecenieSerwisowe.objects.all()
    else:
        messages.error(request, 'Brak dostępu do zleceń.')
        return redirect('home')

    return render(request, 'zlecenia.html', {'zlecenia': zlecenia})


@login_required
def przyjmij_zlecenie(request, zlecenie_id):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może przyjąć zlecenie.'):
        return redirect('home')

    zlecenie = get_object_or_404(ZlecenieSerwisowe, id=zlecenie_id)
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik.rola == 'mechanik':
        zlecenie.mechanik = uzytkownik
        zlecenie.save()

    zmien_status_zlecenia(
        zlecenie,
        'w_realizacji',
        'Zlecenie zostało przyjęte do realizacji przez mechanika.'
    )

    messages.success(request, 'Zlecenie zostało przyjęte do realizacji.')
    return redirect('zlecenia')


@login_required
def dodaj_diagnoze(request):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może dodać diagnozę.'):
        return redirect('home')

    if request.method == 'POST':
        form = DiagnozaForm(request.POST)

        if form.is_valid():
            diagnoza = form.save()

            zmien_status_zlecenia(
                diagnoza.zlecenie,
                'diagnoza',
                'Mechanik dodał diagnozę usterki.'
            )

            messages.success(request, 'Diagnoza została dodana, a status zlecenia zaktualizowany.')
            return redirect('zlecenia')
    else:
        form = DiagnozaForm()

    return render(request, 'dodaj_diagnoze.html', {'form': form})


@login_required
def dodaj_raport(request):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może dodać raport.'):
        return redirect('home')

    if request.method == 'POST':
        form = RaportNaprawyForm(request.POST)

        if form.is_valid():
            raport = form.save()

            zmien_status_zlecenia(
                raport.zlecenie,
                'gotowe',
                'Dodano raport naprawy. Rower jest gotowy do odbioru.'
            )

            messages.success(request, 'Raport naprawy został dodany, a status zlecenia ustawiono jako gotowe.')
            return redirect('zlecenia')
    else:
        form = RaportNaprawyForm()

    return render(request, 'dodaj_raport.html', {'form': form})


@login_required
def dodaj_zuzyta_czesc(request):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może rejestrować zużyte części.'):
        return redirect('home')

    if request.method == 'POST':
        form = ZuzytaCzescForm(request.POST)

        if form.is_valid():
            zuzyta_czesc = form.save(commit=False)
            czesc = zuzyta_czesc.czesc

            if zuzyta_czesc.ilosc <= 0:
                messages.error(request, 'Ilość zużytych części musi być większa od zera.')
                return render(request, 'dodaj_zuzyta_czesc.html', {'form': form})

            if zuzyta_czesc.ilosc > czesc.stan_magazynowy:
                messages.error(
                    request,
                    f'Brak wystarczającej liczby części w magazynie. Dostępne: {czesc.stan_magazynowy}.'
                )
                return render(request, 'dodaj_zuzyta_czesc.html', {'form': form})

            zuzyta_czesc.save()

            czesc.stan_magazynowy -= zuzyta_czesc.ilosc
            czesc.save()

            zmien_status_zlecenia(
                zuzyta_czesc.zlecenie,
                'naprawa',
                f'Użyto części: {zuzyta_czesc.czesc}, ilość: {zuzyta_czesc.ilosc}.'
            )

            messages.success(request, 'Zużyta część została zapisana, a stan magazynowy zaktualizowany.')
            return redirect('zlecenia')
    else:
        form = ZuzytaCzescForm()

    return render(request, 'dodaj_zuzyta_czesc.html', {'form': form})
        
@login_required
def dodaj_czesc(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może dodać część.'):
        return redirect('home')

    if request.method == 'POST':
        form = CzescForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Część została dodana.')
            return redirect('czesci')
    else:
        form = CzescForm()

    return render(request, 'dodaj_czesc.html', {'form': form})


@login_required
def zamowienia_czesci(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Brak dostępu do zamówień części.'):
        return redirect('home')

    zamowienia = ZamowienieCzesci.objects.all().order_by('-data_zamowienia')
    return render(request, 'zamowienia_czesci.html', {'zamowienia': zamowienia})


@login_required
def dodaj_zamowienie_czesci(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może dodać zamówienie części.'):
        return redirect('home')

    if request.method == 'POST':
        form = ZamowienieCzesciForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Zamówienie części zostało dodane.')
            return redirect('zamowienia_czesci')
    else:
        form = ZamowienieCzesciForm()

    return render(request, 'dodaj_zamowienie_czesci.html', {'form': form})
    
@login_required
def szczegoly_zlecenia(request, zlecenie_id):
    zlecenie = get_object_or_404(ZlecenieSerwisowe, id=zlecenie_id)
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'klient' and zlecenie.zgloszenie.klient != uzytkownik:
        messages.error(request, 'Nie masz dostępu do tego zlecenia.')
        return redirect('home')

    if uzytkownik.rola == 'mechanik' and zlecenie.mechanik != uzytkownik:
        messages.error(request, 'Nie masz dostępu do tego zlecenia.')
        return redirect('home')

    if uzytkownik.rola == 'magazynier':
        messages.error(request, 'Magazynier nie ma dostępu do szczegółów zlecenia.')
        return redirect('home')

    context = {
        'zlecenie': zlecenie,
        'diagnozy': zlecenie.diagnozy.all(),
        'raporty': zlecenie.raporty.all(),
        'zuzyte_czesci': zlecenie.zuzyte_czesci.all(),
        'platnosci': zlecenie.platnosci.all(),
        'powiadomienia': zlecenie.powiadomienia.all(),
        'historia_statusow': zlecenie.historia_statusow.all().order_by('-data_zmiany'),
    }

    return render(request, 'szczegoly_zlecenia.html', context)
    
@login_required
def powiadomienia(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'admin':
        powiadomienia = Powiadomienie.objects.all().order_by('-data_wyslania')
    else:
        powiadomienia = Powiadomienie.objects.filter(uzytkownik=uzytkownik).order_by('-data_wyslania')

    return render(request, 'powiadomienia.html', {'powiadomienia': powiadomienia})
    
@login_required
def platnosci(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'klient':
        platnosci = Platnosc.objects.filter(zlecenie__zgloszenie__klient=uzytkownik)
    elif uzytkownik.rola == 'admin':
        platnosci = Platnosc.objects.all()
    else:
        messages.error(request, 'Brak dostępu do płatności.')
        return redirect('home')

    return render(request, 'platnosci.html', {'platnosci': platnosci})


@login_required
def dodaj_platnosc(request):
    if not wymagaj_roli(request, ['admin'], 'Tylko admin może dodawać płatności.'):
        return redirect('home')

    if request.method == 'POST':
        form = PlatnoscForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Płatność została dodana.')
            return redirect('platnosci')
    else:
        form = PlatnoscForm()

    return render(request, 'dodaj_platnosc.html', {'form': form})
    
@login_required
def dodaj_pozycje_zamowienia(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może dodawać pozycje zamówienia.'):
        return redirect('home')

    if request.method == 'POST':
        form = PozycjaZamowieniaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Pozycja zamówienia została dodana.')
            return redirect('zamowienia_czesci')
    else:
        form = PozycjaZamowieniaForm()

    return render(request, 'dodaj_pozycje_zamowienia.html', {'form': form})
    
@login_required
def zmien_status(request, zlecenie_id):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może zmieniać status zlecenia.'):
        return redirect('home')

    zlecenie = get_object_or_404(ZlecenieSerwisowe, id=zlecenie_id)
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik.rola == 'mechanik' and zlecenie.mechanik != uzytkownik:
        messages.error(request, 'Nie możesz zmienić statusu zlecenia przypisanego do innego mechanika.')
        return redirect('zlecenia')

    if request.method == 'POST':
        form = StatusZleceniaForm(request.POST, instance=zlecenie)

        if form.is_valid():
            nowy_status = form.cleaned_data['status']
            komentarz = form.cleaned_data.get('komentarz') or f'Status zlecenia zmieniono na: {nowy_status}.'

            zmien_status_zlecenia(
                zlecenie,
                nowy_status,
                komentarz
            )

            messages.success(request, 'Status zlecenia został zmieniony.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = StatusZleceniaForm(instance=zlecenie)

    return render(request, 'zmien_status.html', {'form': form, 'zlecenie': zlecenie})