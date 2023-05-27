#!/usr/bin/env python3
from datetime import datetime, timedelta
from enum import Enum
import argparse
import os


def note(args):
    """ Create a note """

    editor = fetch_editor()
    path = construct_filepath(args)
    if is_vi_editor(editor):
        md_prefill = construct_md_prefill(args)
        editor_args = construct_vi_args(md_prefill)
    edit_file(editor, editor_args or '', path or '')


def edit_file(editor, editor_args, filename):
    os.system(f"{editor} {editor_args} {filename}")


def is_vi_editor(editor):
    return editor in ['vi', 'vim', 'nvim']


def fetch_directory(date_prefix):
    slot = 'DAILY' if date_prefix else 'NOTEBOOK'
    return os.getenv(slot)


def fetch_editor():
    return os.getenv('EDITOR')


def construct_vi_args(prefill):
    vi_cmd = f':exe "normal i{prefill}\\<Esc>"'
    return f"-c '{vi_cmd}'"


def construct_md_prefill(args):
    title = ' '.join(args.title or args.positional_args)
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
    if date == DateSpec.now:
        return '%Y-%m-%dT%H:%M:%S'
    elif date in [DateSpec.yesterday, DateSpec.today, DateSpec.tomorrow]:
        return '%Y-%m-%d'
    elif date == DateSpec.month:
        return '%Y-%m'
    elif date == DateSpec.year:
        return '%Y'
    else:
        return None


# prepare dated arguments
def extract_date_offset(args):
    date = args.date[0] if args.date else None
    if date == DateSpec.yesterday:
        return -1
    elif date == DateSpec.tomorrow:
        return +1
    else:
        return None


class DateSpec(str, Enum):
    now = 'now'
    day = 'day'
    yesterday = 'yesterday'
    today = 'today'
    tomorrow = 'tomorrow'
    week = 'week'
    month = 'month'
    year = 'year'


def create_parser():
    parser = argparse.ArgumentParser(prog='note',
                                     description='helps you' +
                                     ' take notes in markdown')
    parser.add_argument('-n', '--named',
                        dest='name',
                        metavar='FILENAME',
                        nargs=1,
                        help='set filename')
    parser.add_argument('-t', '--title',
                        nargs=1,
                        help='set the title')
    parser.add_argument('-d', '--dated',
                        dest='date',
                        metavar='DATESPEC',
                        type=DateSpec,
                        nargs=1,
                        help='select from the following date-specs: \n' +
                             '[ now | yesterday | [to]day ' +
                             '| tomorrow | week | month | year ]')
    parser.add_argument('positional_args',
                        nargs=argparse.REMAINDER,
                        help='positional arguments are taken as default '
                        + 'for title and filename')

    return parser


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    note(args)
