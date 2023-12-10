import argparse

from notebook import Book, Note, Shelf


def make_parser():
    root_parser = argparse.ArgumentParser(
        prog="notebook",
        description="helps you manage your notebooks in markdown",
        epilog="by N. M. Podratz",
    )

    # book group
    book_group = root_parser.add_subparsers(
        title="Commands",
        description="Commands for managing your notebooks",
        dest="command",
        metavar="COMMAND",
    )

    bind_book_parser = book_group.add_parser("bind", help="bind your notebook as PDF")
    bind_book_parser.set_defaults(func=Note.export)
    bind_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to bind"
    )

    create_book_parser = book_group.add_parser("create", help="create a new notebook")
    create_book_parser.add_argument(
        "location",
        nargs="?",
        default="~/Notes",
        help="Provide a location for your new notebook",
    )

    list_books_parser = book_group.add_parser(
        "list",
        help="list your notebooks",
    )
    list_books_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to display"
    )

    open_book_parser = book_group.add_parser(
        "open", help="open your notebook in your editor"
    )
    open_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to open"
    )

    show_book_parser = book_group.add_parser(
        "show", help="show your notebook in Finder"
    )
    show_book_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to show"
    )

    # note group
    note_group = root_parser.add_subparsers(
        title="Editing Commands",
        description="Commands to faciliate working with your notebook",
        dest="editing_command",
    )

    create_note_parser = note_group.add_parser("note", help="create a new note")
    create_note_parser.set_defaults(func=Book.note)

    return root_parser


def parse():
    parser = make_parser()
    args = parser.parse_args()

    book = Book(args.directory) or Shelf.selected_book

    if args.command is None:
        details = book.details
        print(details)

    elif args.command == "bind":
        try:
            book.export("pdf")
        except Exception:
            print("Export to pdf failed")

    elif args.command == "create":
        raise NotImplementedError()

    elif args.command == "list":
        print(Shelf.list())

    if args.command == "note":
        note_title = " ".join(args.title)
        note = book.note(note_title)
        note.open()

    elif args.command == "open":
        book.open()

    elif args.command == "set":
        raise NotImplementedError()

    elif args.command == "show":
        book.show()
