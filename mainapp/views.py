from django.shortcuts import render
from .models import Uzytkownik, Rower, Zgloszenie, Czesc


def home(request):
    context = {
        'liczba_uzytkownikow': Uzytkownik.objects.count(),
        'liczba_rowerow': Rower.objects.count(),
        'liczba_zgloszen': Zgloszenie.objects.count(),
        'liczba_czesci': Czesc.objects.count(),
    }

    return render(request, 'home.html', context)

def rowery(request):
    rowery = Rower.objects.all()
    return render(request, 'rowery.html', {'rowery': rowery})

def zgloszenia(request):
    zgloszenia = Zgloszenie.objects.all()
    return render(request, 'zgloszenia.html', {'zgloszenia': zgloszenia})

def czesci(request):
    czesci = Czesc.objects.all()
    return render(request, 'czesci.html', {'czesci': czesci})