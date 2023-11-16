#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import os
import sys
import warnings

ENABLE_WEEKDAYS = False
ENABLE_SUBDAY_DATES = False
ENABLE_RELATIVE_DATES = True


## MARK: Environment

def fetch_editor():
    try:
        return os.environ['EDITOR']
    except KeyError as e:
        print("Error: EDITOR environment variable needs to be defined", e)


def fetch_directory(date_prefix):
    var_name = 'DAILY_NOTES' if date_prefix else 'NOTES'
    return os.getenv(var_name) or os.getenv('NOTES') or None


## MARK: Note class

class Note:
    @classmethod
    def compose_path(cls, directory, filename_components, format='md'):
        if components := list(filter(None, filename_components)):
            filename = f'{"_".join(components)}.{format}'
            return os.path.join(directory, filename)
        else:
            raise ValueError('Insufficient argument list: components need to be provided')

    def __init__(self, filepath: str):
        self.filepath = filepath

    def open(self, editor=None, prefill=None):
        editor = editor or fetch_editor() or 'vi'
        editor_parameters = try_to_construct_editor_parameters(editor, prefill) or ''
        os.system(f"{editor} {editor_parameters} {self.filepath}")


## MARK: Argument parsing

def try_to_construct_editor_parameters(editor, prefill):
    match editor:
        case 'vi' | 'vim' | 'nvim':
            return construct_vi_parameters(prefill)
        case _:
            # other editors are not yet supported -> edit file without prefill
            return None

def construct_vi_parameters(prefill):
    vi_cmd = f':set filetype=markdown|set path+=**|:exe "$normal A{prefill}"'
    return f"-c '{vi_cmd}'"

def construct_header(args):
    if not args.TITLE:
        return None

    def format_heading(level, title):
        return ('#' * level) + ' ' + title.strip(' ')
    title = ' '.join(args.TITLE)
    headings = title.split('/')
    prefixed_headings = map(
            lambda pair: format_heading(pair[0], pair[1]),
            enumerate(headings, start=1))
    return '\n\n'.join(prefixed_headings)


def fetch_body(args):
    """gets the body from std-in"""
    if not os.isatty(args.input.fileno()):
        return ''.join(args.input.readlines())
    else:
        return ''


def construct_md_prefill(args):
    """ Fills a markdown template from hierarchical arguments """
    components = []
    if header := construct_header(args):
        components.append(header)
    if body := fetch_body(args):
        components.append(body)
    return '\n\n'.join(components)



def try_to_construct_filepath(args):
    date_prefix = construct_date_string(args)
    name_appendix = args.name
    if date_prefix or name_appendix:
        directory = fetch_directory(date_prefix)
        note_path = Note.compose_path(directory, [date_prefix, name_appendix])
        return note_path
    else:
        return None


def construct_date_string(args):
    date = datetime.now()

    if date_offset := extract_date_offset(args):
        date += timedelta(date_offset)

    if date_format_string := extract_date_format_string(args):
        return date.strftime(date_format_string)


def extract_date_format_string(args):
    date = args.date
    if date in ['second', 'now']:
        return '%Y-%m-%dT%H:%M:%S'
    if date == 'minute':
        return '%Y-%m-%dT%H:%M'
    if date == 'hour':
        return '%Y-%m-%dT%H'
    elif date in ['day', 'yesterday', 'today', 'tomorrow']:
        return '%Y-%m-%d'
    elif date == 'week':
        return '%Y-W%V'
    elif date == 'weekday':
        return '%Y-W%V-%w'  # %V is iso, %U from sunday, %W from monday
    elif date == 'month':
        return '%Y-%m'
    elif date == 'year':
        return '%Y'
    else:
        return None


# prepare dated arguments
def extract_date_offset(args):
    date = args.date[0] if args.date else None
    if date == 'yesterday':
        return -1
    elif date == 'tomorrow':
        return +1
    else:
        return None


def _parser():
    formatter = make_wide_formatter(argparse.ArgumentDefaultsHelpFormatter)
    parser = argparse.ArgumentParser(formatter_class=formatter,
                                     description='take notes in markdown')

    parser.add_argument('-d', '--date',
                        metavar='DATE',
                        choices=prepare_date_choices(),
                        help='provide a date')

    parser.add_argument('-n', '--name',
                        help='provide a name')

    parser.add_argument('-i', '--input',
                        nargs='?',
                        type=argparse.FileType(),
                        default=sys.stdin,
                        help='provide input')

    parser.add_argument('TITLE',
                        nargs=argparse.REMAINDER,
                        help='set your note\'s title')

    return parser


def make_wide_formatter(formatter, w=120, h=36):
    """Return a wider HelpFormatter, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {'width': w, 'max_help_position': h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter


def prepare_date_choices():
    date_choices = ['now', 'second', 'minute', 'hour', 'day',
                    'weekday', 'week', 'month', 'year',
                    'yesterday', 'today', 'tomorrow']
    unwanted = []
    if not ENABLE_SUBDAY_DATES:
        unwanted.extend(['second', 'minute', 'hour'])
    if not ENABLE_WEEKDAYS:
        unwanted.extend(['week', 'weekday'])
    if not ENABLE_RELATIVE_DATES:
        unwanted.extend(['now', 'yesterday', 'today', 'tomorrow'])
    return [choice for choice in date_choices if choice not in unwanted]


def main():
    parser = _parser()
    args = parser.parse_args()

    # create note
    filepath = try_to_construct_filepath(args) or ''
    note = Note(filepath)

    # open note
    prefill = construct_md_prefill(args)
    note.open(prefill=prefill)


if __name__ == '__main__':
    main()
