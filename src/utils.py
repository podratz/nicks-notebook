import os
import sys
from os import path

from .book import Book


def fetch_directory(date_prefix):
    slot = "DAILY" if date_prefix else "NOTEBOOK"
    return os.getenv(slot)


def fetch_editor():
    return os.getenv("EDITOR")


def fetch_pager():
    return os.getenv("PAGER")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else ""
    book = Book(path)
    book.list_notes()
