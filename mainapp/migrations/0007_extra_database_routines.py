from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
    ('mainapp', '0006_powiadomienie_czy_odczytane'),
]

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE OR REPLACE FUNCTION policz_nieodczytane_powiadomienia(p_uzytkownik_id integer)
            RETURNS integer AS $$
            DECLARE
                v_liczba integer;
            BEGIN
                SELECT COUNT(*)
                INTO v_liczba
                FROM mainapp_powiadomienie
                WHERE uzytkownik_id = p_uzytkownik_id
                  AND czy_odczytane = FALSE;

                RETURN COALESCE(v_liczba, 0);
            END;
            $$ LANGUAGE plpgsql;


            CREATE OR REPLACE FUNCTION czy_czesc_wymaga_zamowienia(p_czesc_id integer)
            RETURNS boolean AS $$
            DECLARE
                v_wymaga boolean;
            BEGIN
                SELECT stan_magazynowy <= stan_minimalny
                INTO v_wymaga
                FROM mainapp_czesc
                WHERE id = p_czesc_id;

                IF v_wymaga IS NULL THEN
                    RAISE EXCEPTION 'Czesc o id % nie istnieje.', p_czesc_id;
                END IF;

                RETURN v_wymaga;
            END;
            $$ LANGUAGE plpgsql;


            CREATE OR REPLACE PROCEDURE oznacz_powiadomienia_jako_odczytane_sql(p_uzytkownik_id integer)
            LANGUAGE plpgsql
            AS $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM mainapp_uzytkownik
                    WHERE id = p_uzytkownik_id
                ) THEN
                    RAISE EXCEPTION 'Uzytkownik o id % nie istnieje.', p_uzytkownik_id;
                END IF;

                UPDATE mainapp_powiadomienie
                SET czy_odczytane = TRUE
                WHERE uzytkownik_id = p_uzytkownik_id;
            END;
            $$;


            CREATE OR REPLACE PROCEDURE ustaw_status_zamowienia_czesci_sql(
                p_zamowienie_id integer,
                p_status varchar
            )
            LANGUAGE plpgsql
            AS $$
            BEGIN
                IF p_status IS NULL OR length(trim(p_status)) = 0 THEN
                    RAISE EXCEPTION 'Status zamowienia nie moze byc pusty.';
                END IF;

                IF NOT EXISTS (
                    SELECT 1
                    FROM mainapp_zamowienieczesci
                    WHERE id = p_zamowienie_id
                ) THEN
                    RAISE EXCEPTION 'Zamowienie czesci o id % nie istnieje.', p_zamowienie_id;
                END IF;

                UPDATE mainapp_zamowienieczesci
                SET status = p_status
                WHERE id = p_zamowienie_id;
            END;
            $$;


            CREATE OR REPLACE FUNCTION sprawdz_stan_czesci_trigger()
            RETURNS trigger AS $$
            BEGIN
                IF NEW.stan_magazynowy < 0 THEN
                    RAISE EXCEPTION 'Stan magazynowy czesci nie moze byc ujemny.';
                END IF;

                IF NEW.stan_minimalny < 0 THEN
                    RAISE EXCEPTION 'Stan minimalny czesci nie moze byc ujemny.';
                END IF;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trg_sprawdz_stan_czesci ON mainapp_czesc;

            CREATE TRIGGER trg_sprawdz_stan_czesci
            BEFORE INSERT OR UPDATE ON mainapp_czesc
            FOR EACH ROW
            EXECUTE FUNCTION sprawdz_stan_czesci_trigger();


            CREATE OR REPLACE FUNCTION sprawdz_kwote_platnosci_trigger()
            RETURNS trigger AS $$
            BEGIN
                IF NEW.kwota IS NULL OR NEW.kwota <= 0 THEN
                    RAISE EXCEPTION 'Kwota platnosci musi byc wieksza od 0.';
                END IF;

                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;

            DROP TRIGGER IF EXISTS trg_sprawdz_kwote_platnosci ON mainapp_platnosc;

            CREATE TRIGGER trg_sprawdz_kwote_platnosci
            BEFORE INSERT OR UPDATE ON mainapp_platnosc
            FOR EACH ROW
            EXECUTE FUNCTION sprawdz_kwote_platnosci_trigger();
            """,
            reverse_sql="""
            DROP TRIGGER IF EXISTS trg_sprawdz_stan_czesci ON mainapp_czesc;
            DROP TRIGGER IF EXISTS trg_sprawdz_kwote_platnosci ON mainapp_platnosc;

            DROP FUNCTION IF EXISTS sprawdz_stan_czesci_trigger();
            DROP FUNCTION IF EXISTS sprawdz_kwote_platnosci_trigger();

            DROP PROCEDURE IF EXISTS oznacz_powiadomienia_jako_odczytane_sql(integer);
            DROP PROCEDURE IF EXISTS ustaw_status_zamowienia_czesci_sql(integer, varchar);

            DROP FUNCTION IF EXISTS policz_nieodczytane_powiadomienia(integer);
            DROP FUNCTION IF EXISTS czy_czesc_wymaga_zamowienia(integer);
            """
        ),
    ]