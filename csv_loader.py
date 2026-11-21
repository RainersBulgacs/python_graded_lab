"""Reading CSV files into flight records and error messages."""
# reference: https://www.geeksforgeeks.org/python/python-remove-duplicates-list/
# reference: https://www.geeksforgeeks.org/python/file-handling-python/
# reference: https://www.w3schools.com/python/python_file_handling.asp
# reference: https://stackoverflow.com/questions/48716446/python-skip-header-row-with-csv-reader
# reference: https://stackoverflow.com/questions/14257373/how-to-skip-the-headers-when-processing-a-csv-file-using-python
# reference: https://www.geeksforgeeks.org/python/reading-and-writing-csv-files-in-python/
# reference: https://stackoverflow.com/questions/22642674/python-csv-reader-list-comprehension
# reference: https://www.w3schools.com/python/python_try_except.asp
# reference: https://www.w3schools.com/python/python_ref_exceptions.asp
# reference: https://docs.python.org/3/library/os.path.html
# Presentation from lecture 10 (slides 2-5, (open, with)); (slides 6-8, (csv module));
# Presentation from lecture 9 (slides 14-15, (dictionaries))
# Presentation from lecture 8 (slides 23, (enumerate)); (slides 19, (strip))
import csv
import os

from validator import to_record, validate_row

def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records: list[dict] = []
    errors: list[str] = []
# Presentation from lecture 9 (slides 4-5 and 18, (sets, tuples))
# Reference: https://www.geeksforgeeks.org/python/python-remove-duplicates-list/
    seen: set[tuple[str, str]] = set()

    for path in paths:
      name = os.path.basename(path)
# Reference: https://www.geeksforgeeks.org/python/file-handling-python/
# Reference: https://www.w3schools.com/python/python_file_handling.asp
      with open(path, encoding="utf-8-sig", newline=None) as f:
# Presentation from lecture 8 (slides 23, (enumerate)) - gives the 1-based physical line number
        for line_no, raw in enumerate(f, start=1):
          line = raw.rstrip("\r\n")
# Reference: https://stackoverflow.com/questions/48716446/python-skip-header-row-with-csv-reader
# Reference: https://stackoverflow.com/questions/14257373/how-to-skip-the-headers-when-processing-a-csv-file-using-python
          if line_no == 1:
            continue
          stripped = line.strip()
          if not stripped or stripped.startswith("#"):
            continue
# Reference: https://www.geeksforgeeks.org/python/reading-and-writing-csv-files-in-python/
# Reference: https://stackoverflow.com/questions/22642674/python-csv-reader-list-comprehension
# Reference: https://www.w3schools.com/python/python_try_except.asp
# Reference: https://www.w3schools.com/python/python_ref_exceptions.asp
# Presentation from lecture 10 (slides 7, (csv.reader)) - splits the line into fields
          try:
            fields = next(csv.reader([line]))
          except (csv.Error, StopInteration):
            fields = []
          code = validate_row(fields, airports)
          if code is None:
            record = to_record(fields)
            key = (record["flight_id"], record["departure_datetime"])
            if key in seen:
              code = "DUPLICATE_FLIGHT"
            else: 
              seen.add(key)
              records.append(record)
          if code is not None:
            errors.append(f"{name}:{line_no}: {code} | {line}")
    return records, errors