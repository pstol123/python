import argparse
import csv
import random
from pathlib import Path
import sys
import glob
import os

MONTHS = {
    "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April", "May": "May", "Jun": "June",
    "Jul": "July", "Aug": "August", "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December"
}

DAYS = {
    "Mon": "Monday", "Tue": "Tuesday", "Wed": "Wednesday", "Thu": "Thursday", "Fri": "Friday",
    "Sat": "Saturday", "Sun": "Sunday"
}

TIMES = {
    "m": "morning", "e": "evening"
}

#stałe do zapisu Dane.csv
HEADLINE = ['Model', 'Wynik', 'Czas']
VALUES_MODEL = ['A', 'B', 'C']
VALUES_START = 0
VALUES_FINISH = 1000

#konweruje i sprawdza poprawność ścieżki
def convert_path(katalog: Path = ""):
    katalog = Path(katalog)
    if (not katalog.is_dir() or not katalog.exists()):
        print("Błędna ścieżka", file=sys.stderr)
        return
    return katalog

#przygotowuje finalną ścieżkę do pliku
def prepare_path(katalog: Path = ""):
    return os.path.join(convert_path(katalog), 'Dane.csv');

#domyślny katalog odczytu to katalog wyjsciowy
#jeżeli Model != 'A' tp funkcja zwraca 0 (nie sumujemy Czasu)
#w przeciwnym wypadku zwraca warotść czas
def read_csv(odczyt):
    with open(odczyt, 'r') as plik:
        czytelnik = csv.reader(plik)

        j = 0
        for wiersz in czytelnik:
            j = j + 1
            if(j == 2): # odczytujemy drugi wiersz
                #odczytanie wartości wraz z obsługą błędów
                if(len(wiersz) < 3):
                    # za mało kolumn
                    print("Błąd odczytu1", file=sys.stderr)
                    return 0

                if (wiersz[0] == 'A'):
                    try:
                        wynik = int(wiersz[2])
                    except (ValueError, TypeError):
                        #typ niedający się przekonwertować na int
                        print("Błąd odczytu2", file=sys.stderr)
                        return 0
                    return wynik
                else:
                    #model różny od 'A'
                    return 0

        #za mało wierszy
        print("Błąd odczytu3", file=sys.stderr)
        return 0

#funkcja zakłada, że znajdujemy sie we właściwym katalogu
def read_all_csv():
    #wyszukujemy wszystkie pliki
    pom = os.path.join(os.getcwd(), '**', 'Dane.csv');

    #sumujemy
    suma = 0
    for plik in glob.glob(pom, recursive = True):
        plik = Path(plik);
        suma += read_csv(plik)
    return suma

#tworzenie nowego pliku, wyznaczenie i wpisanie danych
#katalog - ścieżka do katalogu, w którym tworzymy plik Dane.csv
#domyślnie tworzymy plik w katalogu wyjściowum
def write_csv(katalog: Path = ""):
    pom = prepare_path(katalog)

    # jeżeli plik Dane.csv już istnieje, to go nadpisujemy
    with open(pom, 'w', newline ='') as plik:
        pisarz = csv.writer(plik)

        #losowanie wartości
        model = random.choice(VALUES_MODEL)
        wynik = random.randint(VALUES_START, VALUES_FINISH)
        czas= random.randint(VALUES_START, VALUES_FINISH)

        #zapis do pliku
        pisarz.writerow(HEADLINE)
        pisarz.writerow([model,wynik, czas])

def parse_args():
    pass

def parse_day_range(parser: argparse.ArgumentParser, range_str: str) -> list[str]:
    """
    Parsuje zakresy dni tygodnia (tj. 'Mon-Wed', 'Fri', 'Tue-Fri', ...).
    Zwraca listę wszystkich dni tygodnia z zakresu.
    Wypisuje błąd parsera i kończy program, jeśli zakres był niepoprawny.
    """

    days = range_str.split("-")
    if len(days) == 1:
        day = days[0]
        if day not in DAYS:
            parser.error(f"Invalid day: {day}")
        return [day]
    elif len(days) == 2:
        day1 = days[0]
        day2 = days[1]

        if day1 not in DAYS:
            parser.error(f"Invalid day: {day1}")
        if day2 not in DAYS:
            parser.error(f"Invalid day: {day2}")

        day1_index = list(DAYS).index(day1)
        day2_index = list(DAYS).index(day2)

        if day1_index > day2_index:
            parser.error(f"Invalid range: {day1}-{day2}")

        return list(DAYS)[day1_index:day2_index + 1]
    else:
        parser.error(f"Invalid range format: {range_str}")


def parse_args():
    """
    Obsługuje parametry skryptu i zwraca je w strukturze słownikowej.
    {
        months: list[str],
        days: list[list[str]],
        times: list[str],
        create: bool,
        json: bool
        day_ranges: list[list[str]]
    }
    """

    parser = argparse.ArgumentParser(
        description="Script to generate a directory structure and read (create) CSV (JSON) files."
    )

    parser.add_argument(
        "--months", nargs="+", required=True, choices=MONTHS,
        help="List of months | arbitrary length | e.g. Jan May Feb"
    )
    parser.add_argument(
        "--days", nargs="+", required=True, dest='day_ranges',
        help="Ranges of weekdays | same length as months list | e.g. Mon-Wed Fri Tue-Sun"
    )
    parser.add_argument(
        "--times", nargs="+", default=None, choices=TIMES,
        help="Parts of the day | maximum length is the sum of lengths of the weekdays ranges | m = morning is DEFAULT; e = evening | e.g. m e e m"
    )
    parser.add_argument(
        "--create", action="store_true", help="Create files instead of reading"
    )
    parser.add_argument(
        "--json", action="store_true", help="Use JSON instead of CSV"
    )

    params = parser.parse_args()

    # Sprawdzenie poprawności pojedynczych zakresów dni tygodnia oraz zamiana zakresów na listy dni.
    days: list[list[str]] = []
    for day_range in params.day_ranges:
        days.append(parse_day_range(parser, day_range))

    params.days = days

    # Sprawdzenie długości list miesięcy, dni i pór dnia.
    if len(params.days) != len(params.months):
        parser.error("Number of months should be equal to number of day ranges.")
    if params.times is not None:
        max_length = sum(len(days) for days in params.days)
        if len(params.times) > max_length:
            parser.error(f"Too many parts of the day (--times): got {len(params.times)}, expected max {max_length}")

    return params

if __name__ == '__main__':


    args = parse_args()
    #print(args) # DEBUG
    write_csv() #DEBUG
    print(read_all_csv()) #DEBUG

    #my tests
