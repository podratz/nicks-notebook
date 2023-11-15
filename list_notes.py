import os
import sys
from os import path


def fetch_editor():
    return os.getenv('EDITOR')


def fetch_pager():
    return os.getenv('PAGER')


def open_notes(directory):
    base_dir = os.getenv('NOTEBOOK')
    path = os.path.join(base_dir, directory)
    os.system(f"open -a Finder {path}")


def show_notes(directory):
    base_dir = os.getenv('NOTEBOOK')
    path = os.path.join(base_dir, directory)
    if os.path.isdir(path):
        editor = fetch_editor()
        os.system(f"{editor} {path}")
    else:
        pager = fetch_pager()
        os.system(f"{pager} {path}")


def list_notes(directory):
    base_dir = os.getenv('NOTEBOOK')
    path = os.path.join(base_dir, directory)
    with os.scandir(path) as it:
        entries = list(it)
        entries.sort(key=lambda x: x.name)
        for entry in entries:
            if entry.name.endswith('.md') and entry.is_file():
                # print(entry.name, entry.path)
                print(entry.name.strip('.md'), end='  ')
        print('')


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else ''
    list_notes(path)
