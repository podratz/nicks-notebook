#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
import warnings
from datetime import datetime, timedelta
from typing import Any

from .utils import (
    UnsupportedEditorException,
    construct_editor_params,
    fetch_directory,
    fetch_editor,
)

ENABLE_WEEKDAYS = False
ENABLE_SUBDAY_DATES = False
ENABLE_RELATIVE_DATES = True


class Note:
    """A container for thoughts."""

    @staticmethod
    def compose_path(
        directory: str, filename_components: list[str | None | Any], format: str = "md"
    ):
        if components := list(filter(None, filename_components)):
            filename = f'{"_".join(components)}.{format}'
            return os.path.join(directory, filename)
        else:
            raise ValueError(
                "Insufficient argument list: components need to be provided"
            )

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


def construct_header(args: argparse.Namespace):
    if not args.TITLE:
        return None

    def format_heading(level: int, title: str):
        return ("#" * level) + " " + title.strip(" ")

    title = " ".join(args.TITLE)
    headings = title.split("/")
    prefixed_headings = map(
        lambda pair: format_heading(pair[0], pair[1]), enumerate(headings, start=1)
    )
    return "\n\n".join(prefixed_headings)


def fetch_body(args: argparse.Namespace) -> str:
    """gets the body from std-in"""
    if not os.isatty(args.input.fileno()):
        return "".join(args.input.readlines())
    else:
        return ""


def construct_md_prefill(args: argparse.Namespace) -> str:
    """Fills a markdown template from hierarchical arguments"""
    components = []
    if header := construct_header(args):
        components.append(header)
    if body := fetch_body(args):
        components.append(body)
    return "\n\n".join(components)


def construct_filepath(args: argparse.Namespace) -> str | None:
    date_prefix = construct_date_string(args)
    name_appendix = args.name
    if date_prefix is None and name_appendix is None:
        raise KeyError("Either a date prefix or a name prefix must be provided")
    directory = fetch_directory(date_prefix)
    if not directory:
        return None
    return Note.compose_path(directory, [date_prefix, name_appendix])


def construct_date_string(args: argparse.Namespace) -> str | None:
    date = datetime.now()

    if date_offset := extract_date_offset(args):
        date += timedelta(date_offset)

    if date_format_string := extract_date_format_string(args):
        return date.strftime(date_format_string)


def extract_date_format_string(args: argparse.Namespace) -> str | None:
    date = args.date
    if date in ["second", "now"]:
        return "%Y-%m-%dT%H:%M:%S"
    if date == "minute":
        return "%Y-%m-%dT%H:%M"
    if date == "hour":
        return "%Y-%m-%dT%H"
    elif date in ["day", "yesterday", "today", "tomorrow"]:
        return "%Y-%m-%d"
    elif date == "week":
        return "%Y-W%V"
    elif date == "weekday":
        return "%Y-W%V-%w"  # %V is iso, %U from sunday, %W from monday
    elif date == "month":
        return "%Y-%m"
    elif date == "year":
        return "%Y"
    else:
        return None


# prepare dated arguments
def extract_date_offset(args: argparse.Namespace) -> int | None:
    date = args.date[0] if args.date else None
    if date == "yesterday":
        return -1
    elif date == "tomorrow":
        return +1
    else:
        return None


def prepare_date_choices() -> list[str]:
    date_choices = [
        "now",
        "second",
        "minute",
        "hour",
        "day",
        "weekday",
        "week",
        "month",
        "year",
        "yesterday",
        "today",
        "tomorrow",
    ]
    unwanted = []
    if not ENABLE_SUBDAY_DATES:
        unwanted.extend(["second", "minute", "hour"])
    if not ENABLE_WEEKDAYS:
        unwanted.extend(["week", "weekday"])
    if not ENABLE_RELATIVE_DATES:
        unwanted.extend(["now", "yesterday", "today", "tomorrow"])
    return [choice for choice in date_choices if choice not in unwanted]


def make_wide_formatter(formatter: argparse._FormatterClass, w: int = 120, h: int = 36):
    """Return a wider HelpFormatter, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
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
        choices=prepare_date_choices(),
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
        filepath = construct_filepath(args)
    except KeyError:
        filepath = None

    note = Note(filepath)
    # open note
    prefill = construct_md_prefill(args)
    note.open(prefill=prefill)


if __name__ == "__main__":
    main()
