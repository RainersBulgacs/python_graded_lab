"""Row validation: airport list loading, single-row checks, record building."""
# reference: https://www.geeksforgeeks.org/python/python-regex/
# reference: https://www.geeksforgeeks.org/python/regular-expression-python-examples/
# reference: https://www.geeksforgeeks.org/python/python-regex-cheat-sheet/
# reference: https://www.w3schools.com/python/python_regex.asp
# reference: https://www.geeksforgeeks.org/python/python-datetime-strptime-function/
# reference: https://stackoverflow.com/questions/21437258/how-do-i-parse-a-date-as-an-argument-with-argparse
# reference: https://stackoverflow.com/questions/25470844/specify-date-format-for-python-argparse-input-arguments
# reference: https://www.geeksforgeeks.org/python/python-datetime-module/
# reference: https://www.w3schools.com/python/python_datetime.asp
# reference: https://www.w3schools.com/python/ref_module_datetime.asp
# reference: https://docs.python.org/3/library/re.html
# Presentation from lecture 10 (slides 13-18, (modules, import)); (slides 17, (datetime)); (slides 19-21, (try, except))
# Presentation from lecture 8 (slides 2-6, (functions, parameters, return)); (slides 25, (docstrings))
# Presentation from lecture 9 (slides 23-27, (comprehensions))
import math
import re
from datetime import datetime

# reference: https://www.geeksforgeeks.org/python/python-regex/
# reference: https://www.geeksforgeeks.org/python/regular-expression-python-examples/
# reference: https://www.geeksforgeeks.org/python/python-regex-cheat-sheet/
# reference: https://www.w3schools.com/python/python_regex.asp
FLIGHT_ID_RE = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT_RE = re.compile(r"[A-Z]{3}")
DATETIME_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")
DATETIME_FORMAT = "%Y-%m-%d %H:%M"

def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    airpots = set()
# Presentation from lecture 10 (slides 3-5, (with open, reading a file line by line))
    # raise NotImplementedError
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            c = line.strip() # Presentation from lecture 8 (slides 19, (strip))
            if not c or c.startswith("#"):
                continue
            airpots.add(c)
    return airpots

def parse_price(text: str) -> float | None:
# Presentation from lecture 10 (slides 19-21, (try, except, a conversion that can fail))
    try:
        value = float(text)
    except ValueError:
        return None
    return value if math.isfinite(value) else None

def parse_datetime(text: str) -> datetime   | None:
    if not DATETIME_RE.fullmatch(text):
        return None
# Reference: https://www.geeksforgeeks.org/python/python-datetime-strptime-function/
# Reference: https://stackoverflow.com/questions/21437258/how-do-i-parse-a-date-as-an-argument-with-argparse
# Reference: https://stackoverflow.com/questions/25470844/specify-date-format-for-python-argparse-input-arguments
# Reference: https://www.geeksforgeeks.org/python/python-datetime-module/
# Reference: https://www.w3schools.com/python/python_datetime.asp
# Reference: https://www.w3schools.com/python/ref_module_datetime.asp
# Presentation from lecture 10 (slides 17 and 20, (datetime, try/except))
    try:
        return datetime.strptime(text, DATETIME_FORMAT)
    except ValueError:
        return None

def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    # raise NotImplementedError
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"
# Presentation from lecture 9 (slides 23-27, (comprehensions)) - generator expression with strip()
    flight_id, origin, destination, dep, arr, price = (f.strip() for f in fields)
    if not all((flight_id, origin, destination, dep, arr, price)):
        return "MISSING_FIELD"
    if not FLIGHT_ID_RE.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not AIRPORT_RE.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT_RE.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"
    dep_dt = parse_datetime(dep)
    if dep_dt is None:
        return "INVALID_DEPARTURE"
    arr_dt = parse_datetime(arr)
    if arr_dt is None:
        return "INVALID_ARRIVAL"
    if arr_dt <= dep_dt:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"
    value = parse_price(price)
    if value is None:
        return "INVALID_PRICE"
    if value <= 0:
        return "NON_POSITIVE_PRICE"
    return None

def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    # raise NotImplementedError

    flight_id, origin, destination, dep, arr, price = (f.strip() for f in fields)
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": dep,
        "arrival_datetime": arr,
        "price": float(price),
    }
