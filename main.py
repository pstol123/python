import argparse

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

def read_csv():
    pass

def write_csv():
    pass
    #testtesttes
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
    print(args) # DEBUG

