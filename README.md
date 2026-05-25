# Bike Service Management System

A Django web application for managing a bicycle service workshop. The system supports customer registration, bicycle records, service requests, repair orders, spare parts inventory, payments, notifications, and service order status history.

## Authors

- Karol Czołpiński
- GC
- KP

## Tech Stack

- Python
- Django
- Django ORM
- PostgreSQL
- HTML / CSS
- Django Templates

Required packages:

```bash
pip install django psycopg2-binary
```

## Features

The system supports four roles:

- **Customer** — registers an account, adds bicycles, creates service requests, views own orders, notifications, payments, and status history.
- **Mechanic** — handles assigned service orders, adds diagnoses, repair reports, used parts, and updates order statuses.
- **Warehouse Manager** — manages spare parts, part orders, and order items.
- **Application Administrator** — manages users, assigns roles, and has access to the application admin panel.

The technical Django Admin panel is available at:

```text
/admin/
```

## Main Routes

```text
/                                  home page
/login/                            login
/logout/                           logout
/rejestracja/                      customer registration

/panel-klienta/                    customer panel
/panel-mechanika/                  mechanic panel
/panel-magazyniera/                warehouse manager panel
/panel-admin/                      application administrator panel

/rowery/                           bicycles
/zgloszenia/                       service requests
/zlecenia/                         service orders
/czesci/                           spare parts
/powiadomienia/                    notifications
/platnosci/                        payments
```

## Data Model

The project contains 25 entities:

```text
Uzytkownik, Rower, Zgloszenie, ZlecenieSerwisowe, Diagnoza,
RaportNaprawy, Czesc, ZuzytaCzesc, Powiadomienie, Magazyn,
Platnosc, Adres, Kontakt, ProducentRoweru, TypRoweru,
KategoriaCzesci, Dostawca, ZamowienieCzesci, PozycjaZamowienia,
HistoriaStatusu, TerminSerwisu, StanowiskoSerwisowe,
UslugaSerwisowa, WykonanaUsluga, NotatkaSerwisowa
```

The database structure is implemented with Django ORM. Relationships are mainly based on `ForeignKey` fields.

Key relationships:

```text
Uzytkownik 1 --- many Rower
Uzytkownik 1 --- many Zgloszenie
Rower 1 --- many Zgloszenie
Zgloszenie 1 --- many ZlecenieSerwisowe
ZlecenieSerwisowe 1 --- many Diagnoza
ZlecenieSerwisowe 1 --- many RaportNaprawy
ZlecenieSerwisowe 1 --- many ZuzytaCzesc
ZlecenieSerwisowe 1 --- many HistoriaStatusu
Czesc 1 --- many ZuzytaCzesc
ZamowienieCzesci 1 --- many PozycjaZamowienia
```

## Service Order Workflow

Available service order statuses:

```text
nowe
w_realizacji
diagnoza
naprawa
gotowe
zakonczone
anulowane
```

Main workflow:

```text
Customer creates a service request
→ system creates a service order
→ mechanic accepts the order
→ mechanic adds a diagnosis
→ mechanic registers used parts
→ mechanic adds a repair report
→ customer can view status history and notifications
```

Each important status change creates a `HistoriaStatusu` record and sends a notification to the customer.

## Local Setup

### 1. Create and activate a virtual environment

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:

```powershell
py -m venv venv
venv\Scripts\Activate.ps1
```

### 2. Install packages

```bash
pip install django psycopg2-binary
```

### 3. Configure PostgreSQL

Default local database configuration:

```text
Database: serwis_rowerowy
User: serwis_user
Password: serwis123
Host: localhost
Port: 5432
```

Create the database:

```bash
psql -U postgres
```

```sql
CREATE USER serwis_user WITH PASSWORD 'serwis123';
CREATE DATABASE serwis_rowerowy OWNER serwis_user;
GRANT ALL PRIVILEGES ON DATABASE serwis_rowerowy TO serwis_user;

\c serwis_rowerowy
GRANT ALL ON SCHEMA public TO serwis_user;
ALTER SCHEMA public OWNER TO serwis_user;
\q
```

### 4. Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Django superuser

```bash
python manage.py createsuperuser
```

### 6. Run the server

```bash
python manage.py runserver
```

Application:

```text
http://127.0.0.1:8000/
```

Django Admin:

```text
http://127.0.0.1:8000/admin/
```

## User Accounts

The project uses two user layers:

- **Django User** — authentication, passwords, sessions, Django Admin access.
- **Application User (`Uzytkownik`)** — business data and role-based access.

For role-based access to work correctly:

```text
Django User username = Uzytkownik login
```

Public registration creates customer accounts only. Employee and administrator accounts are created by the application administrator.

## Test Scenario

```text
1. Customer registers an account.
2. Customer adds a bicycle.
3. Customer creates a service request.
4. System automatically creates a service order.
5. Mechanic accepts the order.
6. Mechanic adds a diagnosis.
7. Mechanic registers used parts.
8. Mechanic adds a repair report.
9. Customer views status history and notifications.
10. Administrator adds a payment.
```

## Security Notes

Authentication is handled by Django Auth. Passwords are stored by Django in hashed form. The `Uzytkownik` model is used for business data and roles, not for real password authentication.
