#!/usr/bin/env python3
import datetime
import glob
import os
import subprocess

from .note import Note
from .utils import fetch_editor, fetch_pager


class Book:
    """A container for notes."""

    def __init__(self, directory):
        self.directory = directory

    def __repr__(self):
        return f"Notebook({self.directory!r})"

    def _latest_modification(self, pattern):
        search_md_path = os.path.join(self.directory, pattern)
        files = glob.glob(search_md_path)
        return max(files, key=lambda file: os.stat(file).st_ctime)

    @property
    def creation_time(self):
        p = subprocess.Popen(
            ["stat", "-f%B", self.directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if p.wait() and p.stderr:
            raise OSError(p.stderr.read().rstrip())
        elif p.stdout:
            return int(p.stdout.read())
        else:
            raise SystemError("File handles not available")

    @property
    def manifest(self) -> None | str:
        """User-specified metadata about the book"""
        filepath = os.path.join(self.directory, ".notebook")
        if not os.path.isfile(filepath):
            return None
        with open(filepath) as f:
            return f.read().strip("\n")

    @property
    def details(self) -> str:
        """Computed metadata about the book."""
        details = ""

        overview = self.manifest or "Notebook"
        details += f"\033[1m{overview}\033[0m ({self.directory})\n"

        epoch = self.creation_time
        date = datetime.datetime.fromtimestamp(epoch)
        details += f"Created in {date.year} "

        today = datetime.date.today()
        full_year_months = (today.year - date.year) * 12
        months_back = full_year_months + (today.month - date.month)
        search_md_path = os.path.join(self.directory, "**/*.md")
        md_count = len(glob.glob(search_md_path))
        details += f"({months_back} months ago), {md_count} pages\n\n"

        details += "Recently edited:\n"
        details += self._latest_modification("**/*.md")

        return details

    def export(self, target_format: str) -> None:
        raise NotImplementedError("export function not yet implemented")

    def list(self):
        if base_dir := os.getenv("NOTEBOOK"):
            path = os.path.join(base_dir, self.directory)
            with os.scandir(path) as it:
                entries = list(it)
                entries.sort(key=lambda x: x.name)
                for entry in entries:
                    if entry.name.endswith(".md") and entry.is_file():
                        # print(entry.name, entry.path)
                        print(entry.name.strip(".md"), end="  ")
                print()
        else:
            raise EnvironmentError("Environment variable $NOTEBOOK is undefined.")

    def note(self, title) -> Note:
        """Creates or amends a note."""
        path = os.path.join(self.directory, title)
        return Note(path)

    def open(self):
        if base_dir := os.getenv("NOTEBOOK"):
            path = os.path.join(base_dir, self.directory)
            os.system(f"open -a Finder {path}")
        else:
            raise EnvironmentError("Environment variable $NOTEBOOK is undefined.")

    def show(self):
        if base_dir := os.getenv("NOTEBOOK"):
            path = os.path.join(base_dir, self.directory)
            if os.path.isdir(path):
                editor = fetch_editor()
                os.system(f"{editor} {path}")
            else:
                pager = fetch_pager()
                os.system(f"{pager} {path}")
        else:
            raise EnvironmentError("Environment variable $NOTEBOOK is undefined.")
