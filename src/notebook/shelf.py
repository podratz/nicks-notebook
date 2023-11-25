from .book import Book


class Shelf:
    """A shelf storing the user's books."""

    @property
    @classmethod
    def current(cls) -> Book:
        """Gets the currently active notebook."""
        with open("/Users/nick/.notebooks") as f:
            directory = f.readline().rstrip("\n")
        return Book(directory)

    @current.setter
    @classmethod
    def current(cls, book: Book) -> None:
        """Sets the currently active notebook."""
        with open("/Users/nick/.notebooks", "r") as file:
            lines = file.readlines()
        with open("/Users/nick/.notebooks", "w") as file:
            file.write(book.directory)
            for line in lines:
                if not line.startswith(book.directory):
                    file.write(line)

    @classmethod
    def list(cls) -> str:
        """Lists all available notebooks of the user"""
        with open("/Users/nick/.notebooks") as f:
            return f.read().strip("\n")
