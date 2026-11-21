"""Running queries against the flight database."""
# reference: https://www.geeksforgeeks.org/python/comprehensions-in-python/
# reference: https://www.w3schools.com/python/python_lambda.asp
# reference: https://www.w3schools.com/python/ref_math_isfinite.asp
# Presentation from lecture 9 (slides 3-6, (lists, tuples, sets, dicts)); (slides 24, (list comprehension)); (slides 28-36, (functional style)); (slides 29-30, (lambda))
# Presentation from lecture 10 (slides 13-18, (importing validator.parse_datetime))
# Presentation from lecture 7 (slides 10-11, (isinstance))
import math

from validator import parse_datetime

RECORD_KEYS = ("flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price")
STRING_KEYS = ("flight_id", "origin", "destination")
DATETIME_KEYS = ("departure_datetime", "arrival_datetime")
NUMBER_KEYS = ("price", "min_price")
ALLOWED_KEYS = set(STRING_KEYS) | set(DATETIME_KEYS) | set(NUMBER_KEYS) | {"sort_by", "order", "limit"}

def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    # raise NotImplementedError
    if not is_valid_query(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}
    result = [flight for flight in db if matches(flight, query)]
    if "sort_by" in query:
# Reference: https://www.w3schools.com/python/python_lambda.asp
# Presentation from lecture 9 (slides 29-30, (lambda)) - as the key function
        result = sorted(result, key=lambda fl: fl[query["sort_by"]],
        reverse=query.get("order", "asc") == "desc")
    if "limit" in query:
        result = result[:query["limit"]]
    return {"query": query, "matches": result}

def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    # raise NotImplementedError
    if isinstance(queries, list):
        return[run_query(db, q) for q in queries]
    return[run_query(db, queries)]

def is_number(value) -> bool:
    # Presentation from lecture 7 (slides 10-11, (isinstance))
    # so it has to be excluded explicitly ("booleans are not numbers").
    return isinstance(value, (int, float)) and not isinstance(value, bool) \
        and math.isfinite(value)

def is_valid_query(query) -> bool:
    """True if the query object follows all the rules."""
    if not isinstance(query, dict):
        return False
    for key, value in query.items():
        if key not in ALLOWED_KEYS:
            return False
        if key in STRING_KEYS:
            if not isinstance(value, str):
                return False
        elif key in DATETIME_KEYS:
            if not isinstance(value, str) or parse_datetime(value) is None:
                return False
        elif key in NUMBER_KEYS:
            if not is_number(value):
                return False
        elif key == "sort_by":
            if not isinstance(value, str) or value not in RECORD_KEYS:
                return False
        elif key == "order":
            if value not in ("asc", "desc") or not isinstance(value, str):
                return False
        elif key == "limit":
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                return False
    if "order" in query and "sort_by" not in query:
        return False
    return True

def matches(flight: dict, q: dict) -> bool:
    for key in STRING_KEYS:
        if key in q and flight[key] != q[key]:
            return False
    if "departure_datetime" in q and flight["departure_datetime"] < q["departure_datetime"]:
        return False
    if "arrival_datetime" in q and flight["arrival_datetime"] > q["arrival_datetime"]:
        return False
    if "price" in q and not flight["price"] <= q["price"]:
        return False
    if "min_price" in q and not flight["price"] >= q["min_price"]:
        return False
    return True