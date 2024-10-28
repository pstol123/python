import argparse
import csv
import random
from pathlib import Path
import sys
import glob
import os
import json

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

# Funkcja generująca ścieżki oraz tworząca/odczytująca pliki
def generate_paths_and_files(args):
    """
    Generuje strukturę katalogów na podstawie miesięcy, dni i pory dnia.
    Tworzy lub odczytuje pliki w tych ścieżkach zgodnie z parametrami.
    """
    for i, month in enumerate(args.months):
        month_dir = Path(month)  # Tworzymy ścieżkę katalogu dla każdego miesiąca
        day_range = args.days[i]  # Pobieramy zakres dni dla danego miesiąca

        for j, day in enumerate(day_range):  # Iterujemy przez dni w każdym miesiącu
            # Określamy porę dnia, domyślnie "rano" jeśli nie jest podana
            time_of_day = args.times[j] if args.times and j < len(args.times) else "r"
            time_folder = TIMES.get(time_of_day, "rano")  # "r" = rano, "w" = wieczor

            # Budujemy kompletną ścieżkę: Miesiąc/Dzień/Pora_dnia
            complete_path = month_dir / DAYS[day] / time_folder

            if args.create:
                # Jeśli podano --create, tworzymy katalogi i pliki
                complete_path.mkdir(parents=True, exist_ok=True)  # Tworzymy katalog jeśli nie istnieje
                if args.json:
                    # Tworzenie pliku JSON
                    write_json(complete_path)
                else:
                    # Tworzenie pliku CSV
                    write_csv(complete_path)
            else:
                # Jeśli tryb odczytu, odczytujemy pliki w zadanych ścieżkach
                if args.json:
                    print(read_all_json(complete_path))
                else:
                    print(read_all_csv(complete_path))


# Funkcje pomocnicze dla JSON do zapisu i odczytu w strukturze 

def write_json(directory: Path):
    """
    Zapisuje plik JSON w podanym katalogu.
    """
    file_path = directory / "Data.json"
    
    data = {
        "Model": random.choice(VALUES_MODEL),
        "Wynik": random.randint(VALUES_START, VALUES_FINISH),
        "Czas": random.randint(VALUES_START, VALUES_FINISH)
    }
    
    # Tworzenie katalogu i zapis do pliku JSON
    directory.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file)


def read_json(file_path: Path):
    """
    Odczytuje dane z pliku JSON i zwraca czas przetwarzania jeśli model to 'A'.
    """
    try:
        with open(file_path, 'r') as json_file:
            data = json.load(json_file)
            # Sprawdzamy czy model to 'A' i zwracamy 'Czas', jeśli dane są poprawne
            # Jeśli plik ma błędny format, zwraca 0.
            if data.get("Model") == 'A':
                return int(data.get("Czas", 0))
            return 0
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        # Zwracamy 0 w przypadku błędnego formatu pliku lub innych błędów odczytu
        print(f"Błąd odczytu pliku JSON: {file_path}", file=sys.stderr)
        return 0


def read_all_json(root_path: Path):
    """
    Przeszukuje wszystkie pliki Dane.json w katalogach podrzędnych, 
    sumuje wartości Czas dla plików, gdzie Model jest 'A'
    """
    total_time = 0
    # Wyszukiwanie wszystkich plików JSON w podkatalogach
    for file_path in root_path.rglob("Dane.json"):
        total_time += read_json(file_path)
    return total_time
    

if __name__ == '__main__':


    args = parse_args()
    generate_paths_and_files(args)
    #print(args) # DEBUG
    write_csv() #DEBUG
    print(read_all_csv()) #DEBUG

    #my tests
