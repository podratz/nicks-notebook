#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import warnings
from datetime import datetime, timedelta
from typing import Callable, TextIO

from .date import Date
from .utils import (
    UnsupportedEditorException,
    construct_editor_params,
    fetch_base_directory,
    fetch_editor,
)


class Note:
    """A container for thoughts."""

    @staticmethod
    def compose_path(directory: str, components: list[str], format: str = "md"):
        if not components:
            raise ValueError(
                "Insufficient argument list: components need to be provided"
            )
        filename = f'{"_".join(components)}.{format}'
        return os.path.join(directory, filename)

    def __init__(self, filepath: str | None):
        self.filepath = filepath

    def edit(self, editor: str, editor_args: str):
        """Edits the note in an editor."""
        os.system(f"{editor} {editor_args} {self.filepath or ''}")

    def export(self, target_format: str):
        """Exports specified file to a specifiable file format."""
        if self.filepath is None:
            raise FileNotFoundError()
        # TODO manage pandoc errors, for example exit status 43 when citations include Snigowski et al. 2000
        options = ["pandoc", self.filepath, "-o", self.filepath + target_format]
        # options += ['--ascii', '-s', '--toc'] # some extra options
        # options += ['--variable=geometry:' + 'a4paper'] # to override the default letter size
        options_string = " ".join(options)
        print(options_string)  # for debugging
        return subprocess.check_call(options_string)

    def open(self, editor: str | None = None, prefill: str | None = None):
        try:
            editor = editor or fetch_editor()
        except KeyError:
            editor = "vi"
        try:
            editor_params = construct_editor_params(editor, prefill)
        except UnsupportedEditorException:
            editor_params = ""

        os.system(f"{editor} {editor_params} {self.filepath or ''}")


## MARK: Argument parsing


def construct_header(title: str) -> str:
    def format_heading(level: int, title: str) -> str:
        return ("#" * level) + " " + title.strip(" ")

    title = " ".join(title)
    headings = title.split("/")
    prefixed_headings = map(
        lambda pair: format_heading(pair[0], pair[1]), enumerate(headings, start=1)
    )
    return "\n\n".join(prefixed_headings)


def fetch_body(input: TextIO) -> str:
    """gets the body from std-in"""
    if not os.isatty(input.fileno()):
        return "".join(input.readlines())
    else:
        return ""


def construct_md_prefill(title: str | None, input: TextIO) -> str:
    """Fills a markdown template from hierarchical arguments"""
    components = []
    if title:
        header = construct_header(title)
        components.append(header)
    if body := fetch_body(input):
        components.append(body)
    return "\n\n".join(components)


def construct_filepath(date_choice: str | None, name_appendix: str | None) -> str:
    if date_choice is None and name_appendix is None:
        raise KeyError("Either a date prefix or a name prefix must be provided")

    date_string = construct_date_string(date_choice) if date_choice else None
    is_dated_note = date_string is not None
    try:
        base_directory = fetch_base_directory(is_dated_note)
    except:
        raise
    filename_components = list(filter(None, [date_string, name_appendix]))
    return Note.compose_path(base_directory, filename_components)


def construct_date_string(date_choice: str) -> str:
    date = datetime.now()

    offset = Date(date_choice).offset_in_days
    date += timedelta(offset)

    try:
        date_format_string = Date(date_choice).format_string
        return date.strftime(date_format_string)
    except ValueError:
        raise


def make_wide_formatter(formatter: Callable, w: int = 120, h: int = 36) -> Callable:
    """Return a wider HelpFormatter, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {"width": w, "max_help_position": h}
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter


def make_parser() -> argparse.ArgumentParser:
    formatter = make_wide_formatter(argparse.ArgumentDefaultsHelpFormatter)
    parser = argparse.ArgumentParser(
        formatter_class=formatter,
        description="take notes in markdown",
        epilog="by N. M. Podratz",
    )

    # options
    parser.add_argument(
        "-d",
        "--date",
        metavar="DATE",
        choices=Date.choices(),
        help="provide a date",
    )
    parser.add_argument("-n", "--name", help="provide a name")
    parser.add_argument(
        "-i",
        "--input",
        nargs="?",
        type=argparse.FileType(),
        default=sys.stdin,
        help="provide input",
    )

    # positional
    parser.add_argument("TITLE", nargs=argparse.REMAINDER, help="set your note's title")

    return parser


def main() -> None:
    parser = make_parser()
    args = parser.parse_args()

    # create note
    try:
        filepath = construct_filepath(args.date, args.name)
    except (KeyError, EnvironmentError):
        filepath = None

    note = Note(filepath)
    # open note
    prefill = construct_md_prefill(args.TITLE, args.input)
    note.open(prefill=prefill)


if __name__ == "__main__":
    main()
