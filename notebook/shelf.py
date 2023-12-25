from .book import Book


class Shelf:
    """A container for books."""

    @classmethod
    def selected_book(cls) -> Book:
        """The currently selected book."""
        with open("/Users/nick/.notebooks") as f:
            directory = f.readline().rstrip("\n")
        return Book(directory)

    @classmethod
    def set_selected_book(cls, book: Book) -> None:
        """Select another book."""
        with open("/Users/nick/.notebooks", "r") as file:
            lines = file.readlines()
        with open("/Users/nick/.notebooks", "w") as file:
            file.write(book.directory)
            for line in lines:
                if not line.startswith(book.directory):
                    file.write(line)

    @classmethod
    def list(cls) -> str:
        """List the available books."""
        with open("/Users/nick/.notebooks") as f:
            return f.read().strip("\n")
