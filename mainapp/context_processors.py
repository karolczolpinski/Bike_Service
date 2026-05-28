from .models import Uzytkownik, Powiadomienie


def uzytkownik_aplikacji(request):
    if not request.user.is_authenticated:
        return {
            'uzytkownik_aplikacji': None
        }

    uzytkownik = Uzytkownik.objects.filter(login=request.user.username).first()

    return {
        'uzytkownik_aplikacji': uzytkownik
    }
    
def powiadomienia_context(request):
    liczba_nieodczytanych_powiadomien = 0

    if request.user.is_authenticated:
        uzytkownik = Uzytkownik.objects.filter(
            login=request.user.username
        ).first()

        if uzytkownik is not None:
            liczba_nieodczytanych_powiadomien = Powiadomienie.objects.filter(
                uzytkownik=uzytkownik,
                czy_odczytane=False
            ).count()

    return {
        'liczba_nieodczytanych_powiadomien': liczba_nieodczytanych_powiadomien,
    }