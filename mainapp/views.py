from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render, get_object_or_404

from django.urls import reverse

from django.contrib.auth import login
from django.db import transaction, connection

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
    AdresForm,
    KontaktForm,
    NotatkaSerwisowaForm,
    TerminSerwisuForm,
    WykonanaUslugaForm,
    UzytkownikProfilForm,
    OperacjaMagazynowaForm,
    DostawcaForm,
    ZlecenieSerwisoweEditForm,
    Diagnoza,
    RaportNaprawy,
    ZuzytaCzesc,
    ZamowienieCzesci,
    PozycjaZamowienia,
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
    Adres,
    Kontakt,
    NotatkaSerwisowa,
    TerminSerwisu,
    WykonanaUsluga,
    Magazyn,
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
    profil = None

    if request.user.is_authenticated:
        profil = Uzytkownik.objects.filter(login=request.user.username).first()

    return render(request, 'home.html', {
        'profil': profil,
    })

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

    if uzytkownik.rola == 'admin':
        rowery = Rower.objects.all()

    elif uzytkownik.rola == 'klient':
        rowery = Rower.objects.filter(klient=uzytkownik)

    elif uzytkownik.rola == 'mechanik':
        rowery = Rower.objects.filter(
            zgloszenie__zlecenieserwisowe__mechanik=uzytkownik
        ).distinct()

    else:
        messages.error(request, 'Brak dostępu do listy rowerów.')
        return redirect('home')

    return render(request, 'rowery.html', {
        'rowery': rowery,
    })


@login_required
def zgloszenia(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'admin':
        zgloszenia = Zgloszenie.objects.all()

    elif uzytkownik.rola == 'klient':
        zgloszenia = Zgloszenie.objects.filter(klient=uzytkownik)

    elif uzytkownik.rola == 'mechanik':
        zgloszenia = Zgloszenie.objects.filter(
            zlecenieserwisowe__mechanik=uzytkownik
        ).distinct()

    else:
        messages.error(request, 'Brak dostępu do zgłoszeń.')
        return redirect('home')

    zgloszenia = zgloszenia.order_by('-id')

    return render(request, 'zgloszenia.html', {
        'zgloszenia': zgloszenia,
    })

@login_required
def czesci(request):
    if not wymagaj_roli(request, ['mechanik', 'magazynier', 'admin'], 'Brak dostępu do magazynu części.'):
        return redirect('home')

    czesci = Czesc.objects.all()
    return render(request, 'czesci.html', {'czesci': czesci})
    
@login_required
def szczegoly_czesci(request, czesc_id):
    if not wymagaj_roli(request, ['mechanik', 'magazynier', 'admin'], 'Brak dostępu do szczegółów części.'):
        return redirect('home')

    czesc = get_object_or_404(Czesc, id=czesc_id)

    zuzycia = ZuzytaCzesc.objects.filter(czesc=czesc).select_related('zlecenie').order_by('-id')
    operacje = Magazyn.objects.filter(czesc=czesc).order_by('-id')
    pozycje_zamowien = PozycjaZamowienia.objects.filter(czesc=czesc).select_related('zamowienie').order_by('-id')

    return render(request, 'szczegoly_czesci.html', {
        'czesc': czesc,
        'zuzycia': zuzycia,
        'operacje': operacje,
        'pozycje_zamowien': pozycje_zamowien,
    })


@login_required
def edytuj_czesc(request, czesc_id):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może edytować części.'):
        return redirect('home')

    czesc = get_object_or_404(Czesc, id=czesc_id)

    if request.method == 'POST':
        form = CzescForm(request.POST, instance=czesc)

        if form.is_valid():
            form.save()
            messages.success(request, 'Część została zaktualizowana.')
            return redirect('szczegoly_czesci', czesc_id=czesc.id)
    else:
        form = CzescForm(instance=czesc)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Edytuj część: {czesc.nazwa}',
        'przycisk': 'Zapisz zmiany',
        'powrot_url': reverse('szczegoly_czesci', args=[czesc.id]),
    })

@login_required
def zuzyte_czesci(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola not in ['mechanik', 'admin']:
        messages.error(request, 'Brak dostępu do zużytych części.')
        return redirect('home')

    if uzytkownik.rola == 'admin':
        zuzyte_czesci = ZuzytaCzesc.objects.select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
            'czesc',
        ).order_by('-id')
    else:
        zuzyte_czesci = ZuzytaCzesc.objects.filter(
            zlecenie__mechanik=uzytkownik
        ).select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
            'czesc',
        ).order_by('-id')

    return render(request, 'zuzyte_czesci.html', {
        'zuzyte_czesci': zuzyte_czesci,
    })

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
def diagnozy(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola not in ['mechanik', 'admin']:
        messages.error(request, 'Brak dostępu do diagnoz.')
        return redirect('home')

    if uzytkownik.rola == 'admin':
        diagnozy = Diagnoza.objects.select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
        ).order_by('-data_diagnozy')
    else:
        diagnozy = Diagnoza.objects.filter(
            zlecenie__mechanik=uzytkownik
        ).select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
        ).order_by('-data_diagnozy')

    return render(request, 'diagnozy.html', {
        'diagnozy': diagnozy,
    })

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
def raporty(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola not in ['mechanik', 'admin']:
        messages.error(request, 'Brak dostępu do raportów napraw.')
        return redirect('home')

    if uzytkownik.rola == 'admin':
        raporty = RaportNaprawy.objects.select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
        ).order_by('-data_raportu')
    else:
        raporty = RaportNaprawy.objects.filter(
            zlecenie__mechanik=uzytkownik
        ).select_related(
            'zlecenie',
            'zlecenie__zgloszenie',
            'zlecenie__zgloszenie__klient',
            'zlecenie__zgloszenie__rower',
        ).order_by('-data_raportu')

    return render(request, 'raporty.html', {
        'raporty': raporty,
    })

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

    koszt_czesci_sql = oblicz_koszt_czesci_z_bazy(zlecenie.id)

    context = {
        'zlecenie': zlecenie,
        'diagnozy': zlecenie.diagnozy.all(),
        'raporty': zlecenie.raporty.all(),
        'zuzyte_czesci': zlecenie.zuzyte_czesci.all(),
        'platnosci': zlecenie.platnosci.all(),
        'powiadomienia': zlecenie.powiadomienia.all(),
        'historia_statusow': zlecenie.historia_statusow.all().order_by('-data_zmiany'),
        'koszt_czesci_sql': koszt_czesci_sql,
    }

    return render(request, 'szczegoly_zlecenia.html', context)
    
@login_required
def powiadomienia(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    lista_powiadomien = Powiadomienie.objects.filter(
        uzytkownik=uzytkownik
    ).order_by('-id')

    Powiadomienie.objects.filter(
        uzytkownik=uzytkownik,
        czy_odczytane=False
    ).update(czy_odczytane=True)

    return render(request, 'powiadomienia.html', {
        'powiadomienia': lista_powiadomien,
    })
    
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

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    if uzytkownik.rola == 'mechanik' and zlecenie.mechanik != uzytkownik:
        messages.error(request, 'Nie możesz zmienić statusu zlecenia przypisanego do innego mechanika.')
        return redirect('zlecenia')

    if request.method == 'POST':
        form = StatusZleceniaForm(request.POST, instance=zlecenie)

        if form.is_valid():
            nowy_status = form.cleaned_data['status']
            komentarz = form.cleaned_data.get('komentarz') or f'Status zlecenia zmieniono na: {nowy_status}.'

            zmien_status_zlecenia_przez_procedure(
                zlecenie.id,
                nowy_status,
                komentarz
            )

            messages.success(request, 'Status zlecenia został zmieniony przez procedurę PostgreSQL.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = StatusZleceniaForm(instance=zlecenie)

    return render(request, 'zmien_status.html', {
        'form': form,
        'zlecenie': zlecenie,
    })

@login_required
def moje_dane(request):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    adres = Adres.objects.filter(uzytkownik=uzytkownik).first()
    kontakt = Kontakt.objects.filter(uzytkownik=uzytkownik).first()

    return render(request, 'moje_dane.html', {
        'adres': adres,
        'kontakt': kontakt,
    })


@login_required
def edytuj_adres(request):
    if not wymagaj_roli(request, ['klient', 'mechanik', 'magazynier', 'admin'], 'Brak dostępu do edycji adresu.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    adres = Adres.objects.filter(uzytkownik=uzytkownik).first()

    if request.method == 'POST':
        form = AdresForm(request.POST, instance=adres)

        if form.is_valid():
            adres = form.save(commit=False)
            adres.uzytkownik = uzytkownik
            adres.save()

            messages.success(request, 'Adres został zapisany.')
            return redirect('moje_dane')
    else:
        form = AdresForm(instance=adres)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': 'Edytuj adres',
        'przycisk': 'Zapisz adres',
        'powrot_url': reverse('moje_dane'),
    })

@login_required
def edytuj_kontakt(request):
    if not wymagaj_roli(request, ['klient', 'mechanik', 'magazynier', 'admin'], 'Brak dostępu do edycji kontaktu.'):
        return redirect('home')

    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    kontakt = Kontakt.objects.filter(uzytkownik=uzytkownik).first()

    if request.method == 'POST':
        form = KontaktForm(request.POST, instance=kontakt)

        if form.is_valid():
            kontakt = form.save(commit=False)
            kontakt.uzytkownik = uzytkownik
            kontakt.save()

            messages.success(request, 'Dane kontaktowe zostały zapisane.')
            return redirect('moje_dane')
    else:
        form = KontaktForm(instance=kontakt)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': 'Edytuj kontakt',
        'przycisk': 'Zapisz kontakt',
        'powrot_url': reverse('moje_dane'),
    })
    
def pobierz_zlecenie_dla_mechanika_lub_admina(request, zlecenie_id):
    zlecenie = get_object_or_404(ZlecenieSerwisowe, id=zlecenie_id)
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return None, None

    if uzytkownik.rola == 'admin':
        return zlecenie, uzytkownik

    if uzytkownik.rola == 'mechanik' and zlecenie.mechanik == uzytkownik:
        return zlecenie, uzytkownik

    messages.error(request, 'Nie masz dostępu do tego zlecenia.')
    return None, uzytkownik
    
@login_required
def dodaj_notatke_serwisowa(request, zlecenie_id):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może dodać notatkę.'):
        return redirect('home')

    zlecenie, uzytkownik = pobierz_zlecenie_dla_mechanika_lub_admina(request, zlecenie_id)

    if zlecenie is None:
        return redirect('zlecenia')

    if request.method == 'POST':
        form = NotatkaSerwisowaForm(request.POST)

        if form.is_valid():
            notatka = form.save(commit=False)
            notatka.zlecenie = zlecenie
            notatka.autor = uzytkownik
            notatka.save()

            messages.success(request, 'Notatka serwisowa została dodana.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = NotatkaSerwisowaForm()

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Dodaj notatkę do zlecenia #{zlecenie.id}',
        'przycisk': 'Zapisz notatkę',
        'powrot_url': reverse('szczegoly_zlecenia', args=[zlecenie.id]),
    })
    
@login_required
def dodaj_termin_serwisu(request, zlecenie_id):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może dodać termin.'):
        return redirect('home')

    zlecenie, uzytkownik = pobierz_zlecenie_dla_mechanika_lub_admina(request, zlecenie_id)

    if zlecenie is None:
        return redirect('zlecenia')

    if request.method == 'POST':
        form = TerminSerwisuForm(request.POST)

        if form.is_valid():
            termin = form.save(commit=False)
            termin.zlecenie = zlecenie
            termin.save()

            messages.success(request, 'Termin serwisu został dodany.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = TerminSerwisuForm()

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Dodaj termin do zlecenia #{zlecenie.id}',
        'przycisk': 'Zapisz termin',
        'powrot_url': reverse('szczegoly_zlecenia', args=[zlecenie.id]),
    })
    
@login_required
def dodaj_wykonana_usluga(request, zlecenie_id):
    if not wymagaj_roli(request, ['mechanik', 'admin'], 'Tylko mechanik lub admin może dodać wykonaną usługę.'):
        return redirect('home')

    zlecenie, uzytkownik = pobierz_zlecenie_dla_mechanika_lub_admina(request, zlecenie_id)

    if zlecenie is None:
        return redirect('zlecenia')

    if request.method == 'POST':
        form = WykonanaUslugaForm(request.POST)

        if form.is_valid():
            wykonana_usluga = form.save(commit=False)
            wykonana_usluga.zlecenie = zlecenie

            if not wykonana_usluga.cena_wykonania:
                wykonana_usluga.cena_wykonania = wykonana_usluga.usluga.cena

            wykonana_usluga.save()

            messages.success(request, 'Wykonana usługa została dodana.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = WykonanaUslugaForm()

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Dodaj wykonaną usługę do zlecenia #{zlecenie.id}',
        'przycisk': 'Zapisz usługę',
        'powrot_url': reverse('szczegoly_zlecenia', args=[zlecenie.id]),
    })
    
@login_required
def dodaj_dostawce(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może dodać dostawcę.'):
        return redirect('home')

    if request.method == 'POST':
        form = DostawcaForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Dostawca został dodany.')
            return redirect('panel_magazyniera')
    else:
        form = DostawcaForm()
    
    return render(request, 'formularz.html', {
        'form': form,
        'tytul': 'Dodaj dostawcę',
        'przycisk': 'Zapisz dostawcę',
        'powrot_url': reverse('panel_magazyniera'),
    })


@login_required
def dodaj_operacje_magazynowa(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin może dodać operację magazynową.'):
        return redirect('home')

    if request.method == 'POST':
        form = OperacjaMagazynowaForm(request.POST)

        if form.is_valid():
            operacja = form.save(commit=False)
            czesc = operacja.czesc
            typ_operacji = str(operacja.typ_operacji).lower()

            if typ_operacji in ['przyjecie', 'przyjęcie', 'dostawa', 'plus']:
                czesc.stan_magazynowy += operacja.ilosc
                czesc.save()
                operacja.save()

                messages.success(request, 'Przyjęcie magazynowe zostało zapisane.')
                return redirect('magazyn')

            if typ_operacji in ['wydanie', 'minus']:
                if operacja.ilosc > czesc.stan_magazynowy:
                    messages.error(request, 'Nie można wydać więcej części niż znajduje się w magazynie.')
                    return redirect('dodaj_operacje_magazynowa')

                czesc.stan_magazynowy -= operacja.ilosc
                czesc.save()
                operacja.save()

                messages.success(request, 'Wydanie magazynowe zostało zapisane.')
                return redirect('magazyn')

            operacja.save()
            messages.success(request, 'Operacja magazynowa została zapisana.')
            return redirect('magazyn')
    else:
        form = OperacjaMagazynowaForm()

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': 'Dodaj operację magazynową',
        'przycisk': 'Zapisz operację',
        'powrot_url': reverse('magazyn'),
    })
    
@login_required
def szczegoly_uzytkownika(request, uzytkownik_id):
    if not wymagaj_roli(request, ['admin'], 'Tylko administrator może przeglądać szczegóły użytkownika.'):
        return redirect('home')

    uzytkownik = get_object_or_404(Uzytkownik, id=uzytkownik_id)

    adres = Adres.objects.filter(uzytkownik=uzytkownik).first()
    kontakt = Kontakt.objects.filter(uzytkownik=uzytkownik).first()

    rowery = Rower.objects.filter(klient=uzytkownik)
    zgloszenia = Zgloszenie.objects.filter(klient=uzytkownik)
    zlecenia_mechanika = ZlecenieSerwisowe.objects.filter(mechanik=uzytkownik)

    return render(request, 'szczegoly_uzytkownika.html', {
        'profil': uzytkownik,
        'adres': adres,
        'kontakt': kontakt,
        'rowery': rowery,
        'zgloszenia': zgloszenia,
        'zlecenia_mechanika': zlecenia_mechanika,
    })    
    
@login_required
def uzytkownicy_aplikacji(request):
    if not wymagaj_roli(request, ['admin'], 'Tylko administrator może przeglądać użytkowników.'):
        return redirect('home')

    uzytkownicy = Uzytkownik.objects.all().order_by('rola', 'nazwisko', 'imie')

    return render(request, 'uzytkownicy_aplikacji.html', {
        'uzytkownicy': uzytkownicy,
    })
    
@login_required
def edytuj_uzytkownika_aplikacji(request, uzytkownik_id):
    if not wymagaj_roli(request, ['admin'], 'Tylko administrator może edytować użytkowników.'):
        return redirect('home')

    uzytkownik = get_object_or_404(Uzytkownik, id=uzytkownik_id)

    if request.method == 'POST':
        form = UzytkownikProfilForm(request.POST, instance=uzytkownik)

        if form.is_valid():
            form.save()
            messages.success(request, 'Profil użytkownika został zaktualizowany.')
            return redirect('szczegoly_uzytkownika', uzytkownik_id=uzytkownik.id)
    else:
        form = UzytkownikProfilForm(instance=uzytkownik)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Edytuj profil: {uzytkownik}',
        'przycisk': 'Zapisz profil',
        'powrot_url': reverse('szczegoly_uzytkownika', args=[uzytkownik.id]),
    })
    
@login_required
def magazyn(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin ma dostęp do magazynu.'):
        return redirect('home')

    operacje = Magazyn.objects.select_related('czesc').order_by('-id')

    return render(request, 'magazyn.html', {
        'operacje': operacje,
    })
    
def oblicz_koszt_czesci_z_bazy(zlecenie_id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT oblicz_koszt_czesci(%s)",
            [zlecenie_id]
        )
        wynik = cursor.fetchone()

    if wynik is None:
        return 0

    return wynik[0]
    
def zmien_status_zlecenia_przez_procedure(zlecenie_id, nowy_status, komentarz):
    with transaction.atomic():
        with connection.cursor() as cursor:
            cursor.execute(
                "CALL zmien_status_zlecenia_sql(%s, %s, %s)",
                [zlecenie_id, nowy_status, komentarz]
            )
            
@login_required
def edytuj_zlecenie(request, zlecenie_id):
    if not wymagaj_roli(request, ['admin'], 'Tylko administrator może edytować dane organizacyjne zlecenia.'):
        return redirect('home')

    zlecenie = get_object_or_404(ZlecenieSerwisowe, id=zlecenie_id)

    if request.method == 'POST':
        form = ZlecenieSerwisoweEditForm(request.POST, instance=zlecenie)

        if form.is_valid():
            form.save()
            messages.success(request, 'Zlecenie zostało zaktualizowane.')
            return redirect('szczegoly_zlecenia', zlecenie_id=zlecenie.id)
    else:
        form = ZlecenieSerwisoweEditForm(instance=zlecenie)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Edytuj zlecenie #{zlecenie.id}',
        'przycisk': 'Zapisz zmiany',
        'powrot_url': reverse('szczegoly_zlecenia', args=[zlecenie.id]),
    })
    
@login_required
def szczegoly_roweru(request, rower_id):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    rower = get_object_or_404(Rower, id=rower_id)

    if uzytkownik.rola == 'klient' and rower.klient != uzytkownik:
        messages.error(request, 'Nie masz dostępu do tego roweru.')
        return redirect('rowery')

    if uzytkownik.rola == 'mechanik':
        ma_dostep = ZlecenieSerwisowe.objects.filter(
            zgloszenie__rower=rower,
            mechanik=uzytkownik
        ).exists()

        if not ma_dostep:
            messages.error(request, 'Nie masz dostępu do tego roweru.')
            return redirect('rowery')

    if uzytkownik.rola == 'magazynier':
        messages.error(request, 'Magazynier nie ma dostępu do rowerów klientów.')
        return redirect('home')

    zgloszenia_roweru = Zgloszenie.objects.filter(rower=rower).order_by('-id')
    zlecenia_roweru = ZlecenieSerwisowe.objects.filter(
        zgloszenie__rower=rower
    ).order_by('-id')

    return render(request, 'szczegoly_roweru.html', {
        'rower': rower,
        'zgloszenia_roweru': zgloszenia_roweru,
        'zlecenia_roweru': zlecenia_roweru,
    })
    
@login_required
def edytuj_rower(request, rower_id):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    rower = get_object_or_404(Rower, id=rower_id)

    if uzytkownik.rola == 'klient' and rower.klient != uzytkownik:
        messages.error(request, 'Nie możesz edytować cudzego roweru.')
        return redirect('rowery')

    if uzytkownik.rola not in ['klient', 'admin']:
        messages.error(request, 'Brak dostępu do edycji roweru.')
        return redirect('rowery')

    if request.method == 'POST':
        form = RowerForm(request.POST, instance=rower)

        if form.is_valid():
            edytowany_rower = form.save(commit=False)

            if uzytkownik.rola == 'klient':
                edytowany_rower.klient = uzytkownik

            edytowany_rower.save()
            messages.success(request, 'Dane roweru zostały zaktualizowane.')
            return redirect('szczegoly_roweru', rower_id=rower.id)
    else:
        form = RowerForm(instance=rower)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Edytuj rower: {rower}',
        'przycisk': 'Zapisz zmiany',
        'powrot_url': reverse('szczegoly_roweru', args=[rower.id]),
    })
    
@login_required
def szczegoly_zgloszenia(request, zgloszenie_id):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    zgloszenie = get_object_or_404(Zgloszenie, id=zgloszenie_id)
    zlecenie = ZlecenieSerwisowe.objects.filter(zgloszenie=zgloszenie).first()

    if uzytkownik.rola == 'klient' and zgloszenie.klient != uzytkownik:
        messages.error(request, 'Nie masz dostępu do tego zgłoszenia.')
        return redirect('zgloszenia')

    if uzytkownik.rola == 'mechanik':
        if zlecenie is None or zlecenie.mechanik != uzytkownik:
            messages.error(request, 'Nie masz dostępu do tego zgłoszenia.')
            return redirect('zgloszenia')

    if uzytkownik.rola == 'magazynier':
        messages.error(request, 'Magazynier nie ma dostępu do zgłoszeń serwisowych.')
        return redirect('home')

    return render(request, 'szczegoly_zgloszenia.html', {
        'zgloszenie': zgloszenie,
        'zlecenie': zlecenie,
    })
    
@login_required
def edytuj_zgloszenie(request, zgloszenie_id):
    uzytkownik = pobierz_uzytkownika_aplikacji(request)

    if uzytkownik is None:
        messages.error(request, 'Brak profilu użytkownika aplikacji.')
        return redirect('home')

    zgloszenie = get_object_or_404(Zgloszenie, id=zgloszenie_id)

    if uzytkownik.rola == 'klient' and zgloszenie.klient != uzytkownik:
        messages.error(request, 'Nie możesz edytować cudzego zgłoszenia.')
        return redirect('zgloszenia')

    if uzytkownik.rola not in ['klient', 'admin']:
        messages.error(request, 'Brak dostępu do edycji zgłoszenia.')
        return redirect('zgloszenia')

    if request.method == 'POST':
        form = ZgloszenieForm(request.POST, instance=zgloszenie)

        if 'rower' in form.fields and uzytkownik.rola == 'klient':
            form.fields['rower'].queryset = Rower.objects.filter(klient=uzytkownik)

        if form.is_valid():
            edytowane_zgloszenie = form.save(commit=False)

            if edytowane_zgloszenie.rower:
                edytowane_zgloszenie.klient = edytowane_zgloszenie.rower.klient

            if uzytkownik.rola == 'klient' and edytowane_zgloszenie.klient != uzytkownik:
                messages.error(request, 'Nie możesz przypisać zgłoszenia do cudzego roweru.')
                return redirect('edytuj_zgloszenie', zgloszenie_id=zgloszenie.id)

            edytowane_zgloszenie.save()
            messages.success(request, 'Zgłoszenie zostało zaktualizowane.')
            return redirect('szczegoly_zgloszenia', zgloszenie_id=zgloszenie.id)
    else:
        form = ZgloszenieForm(instance=zgloszenie)

        if 'rower' in form.fields and uzytkownik.rola == 'klient':
            form.fields['rower'].queryset = Rower.objects.filter(klient=uzytkownik)

    return render(request, 'formularz.html', {
        'form': form,
        'tytul': f'Edytuj zgłoszenie #{zgloszenie.id}',
        'przycisk': 'Zapisz zmiany',
        'powrot_url': reverse('szczegoly_zgloszenia', args=[zgloszenie.id]),
    })
    
@login_required
def dostawcy(request):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin ma dostęp do dostawców.'):
        return redirect('home')

    dostawcy = Dostawca.objects.all().order_by('id')

    return render(request, 'dostawcy.html', {
        'dostawcy': dostawcy,
    })
    
@login_required
def szczegoly_zamowienia_czesci(request, zamowienie_id):
    if not wymagaj_roli(request, ['magazynier', 'admin'], 'Tylko magazynier lub admin ma dostęp do szczegółów zamówienia części.'):
        return redirect('home')

    zamowienie = get_object_or_404(ZamowienieCzesci, id=zamowienie_id)

    pozycje = PozycjaZamowienia.objects.filter(
        zamowienie=zamowienie
    ).select_related('czesc').order_by('id')

    return render(request, 'szczegoly_zamowienia_czesci.html', {
        'zamowienie': zamowienie,
        'pozycje': pozycje,
    })
    
