from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from .forms import RowerForm, ZgloszenieForm
from .models import Czesc, Rower, Uzytkownik, Zgloszenie


def home(request):
    context = {
        'liczba_uzytkownikow': Uzytkownik.objects.count(),
        'liczba_rowerow': Rower.objects.count(),
        'liczba_zgloszen': Zgloszenie.objects.count(),
        'liczba_czesci': Czesc.objects.count(),
    }

    return render(request, 'home.html', context)


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
    if request.method == 'POST':
        form = ZgloszenieForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('zgloszenia')
    else:
        form = ZgloszenieForm()

    return render(request, 'dodaj_zgloszenie.html', {'form': form})