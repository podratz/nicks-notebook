#!/usr/bin/env python3
# from mpcurses import mpcurses
import argparse
from list_notes import show_notes, open_notes
from note import Note
import subprocess
import os
import glob
import datetime

class NotebookRegistry:

    @classmethod
    def get_current(cls):
        with open('/Users/nick/.notebooks') as f:
            directory = f.readline().rstrip('\n')
        return Notebook(directory)

    @classmethod
    def set_current(cls, notebook):
        with open('/Users/nick/.notebooks', 'r') as file:
            lines = file.readlines()
        with open('/Users/nick/.notebooks', 'w') as file:
            file.write(notebook.directory)
            for line in lines:
                if not line.startswith(notebook.directory):
                    file.write(line)

class Notebook:

    def __init__(self, directory):
        self.directory = directory

    def note(self, title) -> Note:
        '''Creates or amends a note.'''
        path = os.path.join(self.directory, title)
        return Note(path)

    def get_details(self):
        # Title and location
        if notebook_details := self.get_manifest() or 'Notebook':
            print(f'\033[1m{notebook_details}\033[0m ({self.directory})')

        # Creation date and page count
        creation_epoch = get_creation_time(self.directory)
        creation_date = datetime.datetime.fromtimestamp(creation_epoch)
        today = datetime.date.today()
        relative_months = (today.year - creation_date.year) * 12\
            + (today.month - creation_date.month)
        search_md_path = os.path.join(self.directory, "**/*.md")
        md_count = len(glob.glob(search_md_path))
        print(f'Created in {creation_date.year} '
              f'({relative_months} months ago), {md_count} pages\n')

        # Recently edited
        print('Recently edited:')
        last_edit_file = latest_file_modification(self.directory, '**/*.md')
        print(f'{last_edit_file}')

    def get_manifest(self):
        filepath = os.path.join(self.directory, '.notebook')
        if not os.path.isfile(filepath):
            return None
        with open(filepath) as f:
            return f.read().strip('\n')


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


def list_notebooks():
    with open('/Users/nick/.notebooks') as f:
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



# Until here, we have to refactor into the Notebook class

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


def main():
    parser = _parser()
    args = parser.parse_args()

    if args.command is None:
        notebook = NotebookRegistry.get_current()
        details = notebook.get_details
        print(details)

    elif args.command == 'list':
        print(list_notebooks())

    elif args.command == 'set':
        raise NotImplementedError()

    elif args.command == 'create':
        Notebook(None)

    elif args.command == 'open':
        show_notes(args.directory)

    elif args.command == 'show':
        open_notes(args.directory)

    if args.command == 'note':
        notebook = NotebookRegistry.get_current()
        note_title = ' '.join(args.title)
        note = notebook.note(note_title)
        note.open()

    elif args.command == 'bind':
        notebook = NotebookRegistry.get_current()
        notebook_directory = notebook.directory
        try:
            pandoc(notebook_directory, '.pdf')
        except Exception:
            print('Export to pdf failed')


if __name__ == '__main__':
    main()
