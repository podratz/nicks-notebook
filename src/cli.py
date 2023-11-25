import argparse

from .book import Book
from .note import Note
from .shelf import Shelf


def make_notebook_parser():
    prog = "notebook"
    description = "helps you manage your notebooks in markdown"

    # initialization
    parser = argparse.ArgumentParser(
        prog=prog, description=description, epilog="by N. M. Podratz"
    )
    # interpret remainder as note header
    # parser.add_argument('title', nargs=argparse.REMAINDER)
    # prepare notebook management subparsers
    subparsers = parser.add_subparsers(
        title="Commands",
        description="Commands for managing your notebooks",
        dest="command",
        metavar="COMMAND",
    )
    # create subparser
    create_parser = subparsers.add_parser("create", help="create a new notebook")
    create_parser.add_argument(
        "location",
        nargs="?",
        default="~/Notes",
        help="Provide a location for your new notebook",
    )

    # list subparser
    list_parser = subparsers.add_parser(
        "list",
        # metavar='list',
        help="list your notebooks",
    )

    # open subparser
    open_parser = subparsers.add_parser(
        "open", help="open your notebook in your editor"
    )
    open_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to open"
    )

    # show subparser
    show_parser = subparsers.add_parser("show", help="show your notebook in Finder")
    show_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to show"
    )

    # list_parser.set_defaults(func=list_notes)
    list_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to display"
    )

    # bind subparser
    bind_parser = subparsers.add_parser("bind", help="bind your notebook as PDF")
    bind_parser.set_defaults(func=Note.export)
    bind_parser.add_argument(
        "directory", nargs="?", default="", help="select a subdirectory to bind"
    )
    # pattern matching would be very cool here to for example only print one month, or later everything containing/matching a hashtag

    # prepare note-taking subparsers
    # editing_subparsers = parser.add_subparsers(title='Editing Commands',
    #                                    description='Commands to faciliate working with your notebook',
    #                                    dest='editing_command')
    # # note subparser
    # note_parser = editing_subparsers.add_parser('note', help='create a new note')
    # note_parser.set_defaults(func=note)

    return parser


# bind subparser


def parse():
    parser = make_notebook_parser()
    args = parser.parse_args()

    if args.command is None:
        notebook = Shelf.current
        details = notebook.details
        print(details)

    elif args.command == "list":
        print(Shelf.list())

    elif args.command == "set":
        raise NotImplementedError()

    elif args.command == "create":
        pass

    elif args.command == "open":
        notebook = Book(args.directory)
        notebook.show()

    elif args.command == "show":
        notebook = Book(args.directory)
        notebook.open()

    if args.command == "note":
        notebook = Shelf.current
        note_title = " ".join(args.title)
        note = notebook.note(note_title)
        note.open()

    elif args.command == "bind":
        pass
        # notebook = NotebookRegistry.get_current()
        # notebook_directory = notebook.directory
        # join the notes together, then call pandoc on the joined note.
        # try:
        #     export(notebook_directory, '.pdf')
        # except Exception:
        #     print('Export to pdf failed')
