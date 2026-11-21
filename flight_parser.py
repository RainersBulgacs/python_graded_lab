"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
# Referencees:
# Presentation from lecture 10  (slides 11-12, (json.load, json.dump))
# Presentation from lecture 8 (slides 14, (joining strings))
# https://docs.python.org/3/library/argparse.html
# https://docs.python.org/3/library/os.html
# https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
# https://www.geeksforgeeks.org/python/command-line-option-and-argument-parsing-using-argparse-in-python/
# https://github.com/python/cpython/blob/main/Doc/howto/argparse.rst
# https://github.com/python/cpython/blob/main/Lib/argparse.py
# https://www.geeksforgeeks.org/python/read-write-and-parse-json-using-python/
# https://www.w3schools.com/python/python_json.asp
# https://www.w3schools.com/python/ref_module_json.asp

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from csv_loader import parse_files
from query import run_queries
from validator import load_airports

# TODO: fill in your details: plain ASCII, no spaces or underscores.
STUDENT_ID = "251RDC073"
FIRST_NAME = "Rainers"
LAST_NAME = "Bulgacs"


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    # TODO: parse arguments with argparse (-i, -d, -j, -a, -o, -q, -r).
    # TODO: load or parse the data, write the database and errors.log.
    # TODO: run the queries and write the response file.
    # Remember: remove and close the logging handler before returning,
    # also when returning early because of an error (use try/finally).
    # raise NotImplementedError("main() is not written yet")

# reference: https://www.geeksforgeeks.org/python/command-line-arguments-in-python/
# Reference: https://www.geeksforgeeks.org/python/command-line-option-and-argument-parsing-using-argparse-in-python/
# reference: https://github.com/python/cpython/blob/main/Lib/argparse.py
    parser = argparse.ArgumentParser(
        prog="flight_parser.py",
        description="Validate flight CSV files, store them as JSON and run queries.")
    
    parser.add_argument("-i", metavar="FILE", help="parse a single CSV file")
    parser.add_argument("-d", metavar="FOLDER", help="parse every .csv file in a folder")
    parser.add_argument("-j", metavar="FILE", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", help="airport list file (with -i / -d)")
    parser.add_argument("-o", metavar="FILE", help="output JSON database (default: db.json)")
    parser.add_argument("-q", metavar="FILE", help="JSON file with queries")
    parser.add_argument("-r", metavar="FOLDER", default=".",
    help="folder for the response file (default: current directory)")

    try:
        args = parser.parse_args(argv)
        sources = [s for s in (args.i, args.d, args.j) if s is not None]
        if len(sources) == 0:
            parser.error("one data source is required: -i, -d or -j")
        if len(sources) > 1:
            parser.error("use only one data source: -i, -d or -j")
        if args.j is None and args.a is None:
            parser.error("-a is required with -i and -d")
        if args.j is not None and args.o is not None:
            parser.error("-o cannot be used with -j")
# reference: https://github.com/python/cpython/blob/main/Lib/argparse.py
    except SystemExit as e:  # argparse exits on -h (0) and usage errors (2)
        return e.code if isinstance(e.code, int) else 2

# reference: https://www.geeksforgeeks.org/python/read-write-and-parse-json-using-python/
# reference: https://www.w3schools.com/python/python_json.asp
# reference: https://www.w3schools.com/python/ref_module_json.asp
# Presentation from lecture 10 (slides 11, (json.load, with open))
    try:
        # ------------------------------------------------ database from JSON
        if args.j is not None:

            with open(args.j, encoding="utf-8-sig") as f:
                db = json.load(f)
            if not isinstance(db, list) or not all(isinstance(x, dict) for x in db):
                raise ValueError(f"{args.j} must contain a JSON array of objects")

        # ------------------------------------------------ database from CSV
        else:
            if args.i is not None:
                paths = [args.i]
            else:
                if not os.path.isdir(args.d):
                    raise FileNotFoundError(f"folder not found: {args.d}")
                names = sorted(n for n in os.listdir(args.d)
                               if n.endswith(".csv") and os.path.isfile(os.path.join(args.d, n)))
                if not names:
                    raise FileNotFoundError(f"no .csv files in folder: {args.d}")
                paths = [os.path.join(args.d, n) for n in names]

            airports = load_airports(args.a)
            db_path = args.o if args.o is not None else "db.json"
            log_path = os.path.join(os.path.dirname(db_path), "errors.log")

            logger = logging.getLogger("flight_parser")
            logger.setLevel(logging.INFO)
            handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
            handler.setFormatter(logging.Formatter(
                "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
            logger.addHandler(handler)
            try:
                db, errors = parse_files(paths, airports)
                for message in errors:
                    logger.warning(message)
                logger.info("%d valid rows, %d invalid rows", len(db), len(errors))
# Presentation from lecture 10 (slides 12, (json.dump, with open))
# reference: https://www.geeksforgeeks.org/python/read-write-and-parse-json-using-python/
# reference: https://www.w3schools.com/python/python_json.asp
# reference: https://www.w3schools.com/python/ref_module_json.asp
                with open(db_path, "w", encoding="utf-8") as f:
                    json.dump(db, f, indent=2)
                print(f"{len(db)} valid flights, {len(errors)} invalid rows")
            finally:
                logger.removeHandler(handler)
                handler.close()

        # ------------------------------------------------------- queries
        if args.q is not None:
            with open(args.q, encoding="utf-8-sig") as f:
                queries = json.load(f)
            if not isinstance(queries, (dict, list)):
                raise ValueError(f"{args.q} must contain a query object or an array")
            results = run_queries(db, queries)

            stamp = datetime.now().strftime("%Y%m%d_%H%M")
            name = f"response_{STUDENT_ID}_{FIRST_NAME}_{LAST_NAME}_{stamp}.json"
            response_path = os.path.join(args.r, name)
            with open(response_path, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"Response written to {response_path}")

    except Exception as e:
        if isinstance(e, json.JSONDecodeError):
            msg = f"invalid JSON: {e}"
        elif isinstance(e, FileNotFoundError):
            msg = e.strerror and f"{e.strerror}: {e.filename}" or str(e)
        else:
            msg = str(e)
        print(f"Error: {msg}", file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
