from .models import Uzytkownik


def uzytkownik_aplikacji(request):
    if not request.user.is_authenticated:
        return {
            'uzytkownik_aplikacji': None
        }

    uzytkownik = Uzytkownik.objects.filter(login=request.user.username).first()

    return {
        'uzytkownik_aplikacji': uzytkownik
    }