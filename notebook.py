#!/usr/bin/env python3
# from mpcurses import mpcurses
import argparse
from note import note
from list_notes import show_notes, open_notes
import subprocess
import os
import glob
import datetime


def _parser():
    prog = 'notebook'
    description = 'helps you manage your notebooks in markdown'

    # initialization
    parser = argparse.ArgumentParser(prog=prog, description=description)
    # interpret remainder as note header
    # parser.add_argument('title', nargs=argparse.REMAINDER)
    # prepare notebook management subparsers
    subparsers = parser.add_subparsers(title='Commands',
                                       description='Commands for managing your notebooks',
                                       dest='command',
                                       metavar='COMMAND')
    # create subparser
    create_parser = subparsers.add_parser(
        'create', help='create a new notebook')
    create_parser.add_argument('location', nargs='?', default='~/Notes',
                               help='Provide a location for your new notebook')

    # list subparser
    list_parser = subparsers.add_parser('list',
                                        # metavar='list',
                                        help='list your notebooks')

    # open subparser
    open_parser = subparsers.add_parser(
        'open', help='open your notebook in your editor')
    open_parser.add_argument('directory', nargs='?',
                             default='', help='select a subdirectory to open')

    # show subparser
    show_parser = subparsers.add_parser(
        'show', help='show your notebook in Finder')
    show_parser.add_argument('directory', nargs='?',
                             default='', help='select a subdirectory to show')

    # list_parser.set_defaults(func=list_notes)
    list_parser.add_argument( 'directory',
        nargs='?',
        default='',
         help='select a subdirectory to display')

    # bind subparser
    bind_parser = subparsers.add_parser(
        'bind', help='bind your notebook as PDF')
    bind_parser.set_defaults(func=pandoc)
    bind_parser.add_argument('directory', nargs='?',
                             default='', help='select a subdirectory to bind')
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


def pandoc(filename, extension):
    # TODO manage pandoc errors, for example exit status 43 when citations include Snigowski et al. 2000
    options = ['pandoc', filename, '-o', filename + extension]
    # options += ['--ascii', '-s', '--toc'] # some extra options
    # options += ['--variable=geometry:' + 'a4paper'] # to override the default letter size
    options_string = ' '.join(options)
    print(options_string)  # for debugging
    return subprocess.check_call(options_string)


def edit_file(editor, editor_args, filename):
    os.system(f"{editor} {editor_args} {filename}")


def fetch_directory(date_prefix):
    slot = 'DAILY' if date_prefix else 'NOTEBOOK'
    return os.getenv(slot)


def fetch_editor():
    return os.getenv('EDITOR')


def current_notebook():
    with open('/Users/nick/.notebooks') as f:
        return f.readline().strip('\n')


def list_notebooks():
    with open('/Users/nick/.notebooks') as f:
        return f.read().strip('\n')


def set_notebook(name):
    # search list linearly. If found, move the line to the top and return.
    # if end is reached and notebook is not found, raise error.
    pass


def get_notebook_manifest(path):
    filepath = os.path.join(path, '.notebook')
    if not os.path.isfile(filepath):
        return None
    with open(filepath) as f:
        return f.read().strip('\n')


def get_creation_time(path):
    p = subprocess.Popen(['stat', '-f%B', path],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.wait():
        raise OSError(p.stderr.read().rstrip())
    else:
        return int(p.stdout.read())


def latest_file_modification(notebook_path, pattern):
    search_md_path = os.path.join(notebook_path, pattern)
    files = glob.glob(search_md_path)
    return max(files, key=lambda file: os.stat(file).st_ctime)


def print_notebook_details():
    notebook_path = current_notebook()

    # Title and location
    if notebook_details := get_notebook_manifest(notebook_path) or 'Notebook':
        print(f'\033[1m{notebook_details}\033[0m ({notebook_path})')

    # Creation date and page count
    creation_epoch = get_creation_time(notebook_path)
    creation_date = datetime.datetime.fromtimestamp(creation_epoch)
    today = datetime.date.today()
    relative_months = (today.year - creation_date.year) * 12\
        + (today.month - creation_date.month)
    search_md_path = os.path.join(notebook_path, "**/*.md")
    md_count = len(glob.glob(search_md_path))
    print(f'Created in {creation_date.year} '
          f'({relative_months} months ago), {md_count} pages\n')

    # Recently edited
    print('Recently edited:')
    last_edit_file = latest_file_modification(notebook_path, '**/*.md')
    print(f'{last_edit_file}')


def create_notebook():
    print('Create notebook called')


def main():
    parser = _parser()
    args = parser.parse_args()

    if args.command is None:
        print_notebook_details()

    elif args.command == 'list':
        print(list_notebooks())

    elif args.command == 'set':
        set_notebook()

    elif args.command == 'create':
        create_notebook()

    elif args.command == 'open':
        show_notes(args.directory)

    elif args.command == 'show':
        open_notes(args.directory)

    if args.command == 'note':
        title = ' '.join(args.title)
        note(title=title)

    elif args.command == 'bind':
        input_file = current_notebook()
        try:
            pandoc(input_file, '.pdf')
        except Exception:
            print('Export to pdf failed')


if __name__ == '__main__':
    main()
