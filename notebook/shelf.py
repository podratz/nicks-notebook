from typing import Self

from .book import Book


class Shelf:
    """A container for books."""

    @classmethod
    def default(cls) -> Self:
        return cls()

    @property
    def selected_book(cls) -> Book:
        """The currently selected book."""
        with open("/Users/nick/.notebooks") as f:
            directory = f.readline().rstrip("\n")
        return Book(directory)

    @selected_book.setter
    def selected_book(cls, book: Book) -> None:
        """Select another book."""
        with open("/Users/nick/.notebooks", "r") as file:
            lines = file.readlines()
        with open("/Users/nick/.notebooks", "w") as file:
            file.write(book.directory)
            for line in lines:
                if not line.startswith(book.directory):
                    file.write(line)

    def list(self) -> str:
        """List the available books."""
        with open("/Users/nick/.notebooks") as f:
            return f.read().strip("\n")
