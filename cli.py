#!/usr/bin/env python3
import argparse

from notebook import Book, Note, Shelf
from notebook.note import main as note_main


def make_parser():
    root_parser = argparse.ArgumentParser(
        prog="notebook",
        description="helps you manage your notebooks in markdown",
        epilog="by N. M. Podratz",
    )

    sub_parsers = root_parser.add_subparsers(
        title="Commands",
        description="Commands for managing your notebooks",
        dest="command",
        metavar="COMMAND",
    )

    bind_book_parser = sub_parsers.add_parser("bind", help="bind your notebook as PDF")
    bind_book_parser.set_defaults(func=Note.export)
    bind_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to bind"
    )

    create_book_parser = sub_parsers.add_parser("create", help="create a new notebook")
    create_book_parser.add_argument(
        "location",
        nargs="?",
        default="~/Notes",
        help="Provide a location for your new notebook",
    )

    list_books_parser = sub_parsers.add_parser(
        "list",
        help="list your notebooks",
    )
    list_books_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to display"
    )

    open_book_parser = sub_parsers.add_parser(
        "open", help="open your notebook in your editor"
    )
    open_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to open"
    )

    show_book_parser = sub_parsers.add_parser(
        "show", help="show your notebook in Finder"
    )
    show_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to show"
    )

    # note group
    create_note_parser = sub_parsers.add_parser("note", help="create a new note")
    create_note_parser.set_defaults(func=Book.note)

    return root_parser


def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.command is None:
        book = Shelf.selected_book()
        print(book.details)

    elif args.command == "bind":
        try:
            book = Book(args.directory) or Shelf.selected_book()
            book.export("pdf")
        except Exception:
            print("Export to pdf failed")

    elif args.command == "create":
        raise NotImplementedError()

    elif args.command == "list":
        print(Shelf.list())

    if args.command == "note":
        note_main()

    elif args.command == "open":
        book = Book(args.directory) or Shelf.selected_book()
        book.open()

    elif args.command == "set":
        raise NotImplementedError()

    elif args.command == "show":
        book = Book(args.directory) or Shelf.selected_book()
        book.show()


if __name__ == "__main__":
    main()
