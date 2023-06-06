#!/usr/bin/env python3
from datetime import datetime, timedelta
import argparse
import os
import warnings

ENABLE_WEEKDAYS = False
ENABLE_SUBDAY_DATES = False
ENABLE_RELATIVE_DATES = True


def note(args):
    """ Create a note """

    editor = fetch_editor()
    path = construct_filepath(args)
    if is_vi_editor(editor):
        md_prefill = construct_md_prefill(args)
        editor_args = construct_vi_args(md_prefill)
    edit_file(editor, editor_args or '', path or '')


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


def edit_file(editor, editor_args, filename):
    os.system(f"{editor} {editor_args} {filename}")


def fetch_directory(date_prefix):
    slot = 'DAILY' if date_prefix else 'NOTEBOOK'
    return os.getenv(slot)


def fetch_editor():
    return os.getenv('EDITOR')


def is_vi_editor(editor):
    return editor in ['vi', 'vim', 'nvim']


def construct_vi_args(prefill):
    vi_cmd = f':exe "normal i{prefill}\\<Esc>"'
    return f"-c '{vi_cmd}'"


def construct_md_prefill(args):
    title = ' '.join(args.TITLE or [])
    return f'# {title}\n\n' if title else ''


def construct_filepath(args):
    date_prefix = construct_date_string(args)
    name_appendix = args.name[0] if args.name else None
    if date_prefix or name_appendix:
        directory = fetch_directory(date_prefix)
        return compose_path(directory, [date_prefix, name_appendix])


def construct_date_string(args):
    date = datetime.now()

    if date_offset := extract_date_offset(args):
        date += timedelta(date_offset)

    if date_format_string := extract_date_format_string(args):
        return date.strftime(date_format_string)


def compose_path(directory, filename_components, format='md'):
    if components := list(filter(None, filename_components)):
        filename = f'{"_".join(components)}.{format}'
        return os.path.join(directory, filename)
    else:
        raise ValueError('Insufficient argument list: '
                         + 'components need to be provided')


def extract_date_format_string(args):
    date = args.date[0] if args.date else None
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


def create_parser():
    formatter = make_wide_formatter(argparse.ArgumentDefaultsHelpFormatter)
    parser = argparse.ArgumentParser(prog='note',
                                     allow_abbrev=True,
                                     formatter_class=formatter,
                                     description='take notes in markdown')

    parser.add_argument('-d', '--date',
                        dest='date',
                        choices=prepare_date_choices(),
                        metavar='DATE',
                        nargs=1,
                        help='provide a date')

    parser.add_argument('-n', '--name',
                        dest='name',
                        metavar='NAME',
                        nargs=1,
                        help='provide a name')

    parser.add_argument('TITLE',
                        nargs=argparse.REMAINDER,
                        help='set your note\'s title')

    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    note(args)
