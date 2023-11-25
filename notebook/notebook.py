#!/usr/bin/env python3
# from mpcurses import mpcurses
import argparse
import datetime
import glob
import os
import subprocess

from list_notes import open_notes, show_notes
from note import Note

from .notebook_registry import NotebookRegistry


class Notebook:
    def __init__(self, directory):
        self.directory = directory

    def __repr__(self):
        return f"Notebook({self.directory!r})"

    @property
    def creation_time(self):
        p = subprocess.Popen(
            ["stat", "-f%B", self.directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if p.wait():
            raise OSError(p.stderr.read().rstrip())
        else:
            return int(p.stdout.read())

    def latest_modification(self, pattern):
        search_md_path = os.path.join(self.directory, pattern)
        files = glob.glob(search_md_path)
        return max(files, key=lambda file: os.stat(file).st_ctime)

    @property
    def manifest(self) -> None | str:
        """Gets user-specified metadata about the notebook"""
        filepath = os.path.join(self.directory, ".notebook")
        if not os.path.isfile(filepath):
            return None
        with open(filepath) as f:
            return f.read().strip("\n")

    @property
    def details(self) -> str:
        """Get computed metadata about the notebook."""
        details = ""

        overview = self.manifest or "Notebook"
        details += f"\033[1m{overview}\033[0m ({self.directory})\n"

        epoch = self.creation_time
        date = datetime.datetime.fromtimestamp(epoch)
        details += f"Created in {date.year} "

        today = datetime.date.today()
        months_back = (today.year - date.year) * 12 + (today.month - date.month)
        search_md_path = os.path.join(self.directory, "**/*.md")
        md_count = len(glob.glob(search_md_path))
        details += f"({months_back} months ago), {md_count} pages\n\n"

        details += "Recently edited:\n"
        details += self.latest_modification("**/*.md")

        return details

    def note(self, title) -> Note:
        """Creates or amends a note."""
        path = os.path.join(self.directory, title)
        return Note(path)


# TODO: define on note
def edit(editor, editor_args, filename):
    """Edits the file in an editor."""
    os.system(f"{editor} {editor_args} {filename}")


# TODO: define in utils
def fetch_directory(date_prefix):
    slot = "DAILY" if date_prefix else "NOTEBOOK"
    return os.getenv(slot)


# TODO: define in utils
def fetch_editor():
    return os.getenv("EDITOR")


# Until here, we have to refactor into the Notebook class


def make_parser():
    prog = "notebook"
    description = "helps you manage your notebooks in markdown"

    # initialization
    parser = argparse.ArgumentParser(prog=prog, description=description)
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


def main():
    parser = make_parser()
    args = parser.parse_args()

    if args.command is None:
        notebook = NotebookRegistry.current
        details = notebook.details
        print(details)

    elif args.command == "list":
        print(NotebookRegistry.list())

    elif args.command == "set":
        raise NotImplementedError()

    elif args.command == "create":
        Notebook(None)

    elif args.command == "open":
        show_notes(args.directory)

    elif args.command == "show":
        open_notes(args.directory)

    if args.command == "note":
        notebook = NotebookRegistry.current
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


if __name__ == "__main__":
    main()
