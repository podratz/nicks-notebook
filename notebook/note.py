import os
import subprocess

if __name__ == "note":
    from utils import UnsupportedEditorException, construct_editor_params, fetch_editor
else:
    from .utils import UnsupportedEditorException, construct_editor_params, fetch_editor


class Note:
    """A container for thoughts."""

    def __init__(self, filepath: str | None):
        self.filepath = filepath

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

    @staticmethod
    def compose_path(directory: str, components: list[str], format: str = "md"):
        if not components:
            raise ValueError(
                "Insufficient argument list: components need to be provided"
            )
        filename = f'{"_".join(components)}.{format}'
        return os.path.join(directory, filename)
