from .models import Uzytkownik, Powiadomienie
from django.db import connection, DatabaseError



def uzytkownik_aplikacji(request):
    if not request.user.is_authenticated:
        return {
            'uzytkownik_aplikacji': None
        }

    uzytkownik = Uzytkownik.objects.filter(login=request.user.username).first()

    return {
        'uzytkownik_aplikacji': uzytkownik
    }


def licznik_powiadomien(request):
    if not request.user.is_authenticated:
        return {
            'liczba_nieodczytanych_powiadomien': 0
        }

    uzytkownik = Uzytkownik.objects.filter(
        login=request.user.username
    ).first()

    if uzytkownik is None:
        return {
            'liczba_nieodczytanych_powiadomien': 0
        }

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT policz_nieodczytane_powiadomienia(%s)",
                [uzytkownik.id]
            )
            wynik = cursor.fetchone()

        liczba = wynik[0] if wynik else 0

    except DatabaseError:
        liczba = Powiadomienie.objects.filter(
            uzytkownik=uzytkownik,
            czy_odczytane=False
        ).count()

    return {
        'liczba_nieodczytanych_powiadomien': liczba
    }