#!/usr/bin/env python3
# from mpcurses import mpcurses
import argparse
from note import note
from list_notes import list_notes, show_notes, open_notes
import subprocess
import os

def _parser():
    prog = 'notebook'
    description = 'helps you manage notebooks in markdown'

    # initialization
    parser = argparse.ArgumentParser(prog=prog, description=description)
    
    # interpret remainder as note header
    # parser.add_argument('title', nargs=argparse.REMAINDER)
    
    # prepare subparsers
    subparsers = parser.add_subparsers(title='Commands',
                                       description='Commands to faciliate working with your notebook',
                                       dest='command'
                                       )
    
    # show subparser
    show_parser = subparsers.add_parser('show', help='show the overview of your notes in your editor')
    show_parser.add_argument('directory', nargs='?', default='', help='select a subdirectory to show')
    
    # open subparser
    open_parser = subparsers.add_parser('open', help='open your notes in Finder')
    open_parser.add_argument('directory', nargs='?', default='', help='select a subdirectory to open')
    
    # list subparser
    list_parser = subparsers.add_parser('list',
                                        # metavar='list',
                                        aliases=['ls'],
                                        help='show and list all your notes')
    # list_parser.set_defaults(func=list_notes)
    list_parser.add_argument('directory', nargs='?', default='', help='select a subdirectory to display')
    
    # note subparser
    note_parser = subparsers.add_parser('note', help='create a new note')

    note_parser.set_defaults(func=note)
    bind_parser = subparsers.add_parser('bind',
                                        help='bind your notes into a pdf file')
    bind_parser.set_defaults(func=pandoc)
    bind_parser.add_argument('directory', nargs='?', default='', help='select a subdirectory to bind')
    # pattern matching would be very cool here to for example only print one month, or later everything containing/matching a hashtag
    return parser

# bind subparser
def pandoc(filename, extension):
    # TODO manage pandoc errors, for example exit status 43 when citations include Snigowski et al. 2000
    options = ['pandoc', filename + '.md', '-o', filename + extension]
    options += ['--ascii', '-s', '--toc'] # some extra options
    options += ['--variable=geometry:' + 'a4paper'] # to override the default letter size
    print(options)  # for debugging
    return subprocess.check_call(options)



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
    with open(filepath) as f:
        return f.read().strip('\n')


def main():
    parser = _parser()
    args = parser.parse_args()

    if args.command is None:
        notebook_path = current_notebook()
        print(get_notebook_manifest(notebook_path))
        print(f'Location: {notebook_path}')

    elif args.command in ['list', 'ls']:
        print(list_notebooks())

    elif args.command == 'set':
        set_notebook()

    elif args.command == 'open':
        show_notes(args.directory)

    elif args.command == 'show':
        open_notes(args.directory)

    if args.command == 'note':
        title = ' '.join(args.title)
        note(title=title)

    elif args.command == 'bind':
        input_file = ''
        try:
            pandoc(input_file, 'pdf')
        except Exception:
            print('Export to pdf failed')

if __name__ =='__main__':
    main()
