import os


class UnsupportedEditorException(Exception):
    def __init__(self, editor):
        self.editor = editor
        super().__init__(editor)


def construct_editor_params(editor: str, prefill: str | None) -> str:
    match editor:
        case "vi" | "vim" | "nvim":
            cmd = f':set filetype=markdown|set path+=**|:exe "$normal A{prefill or ""}"'
            return f"-c '{cmd}'"
        case _:
            raise UnsupportedEditorException(editor)


def fetch_editor() -> str:
    try:
        return os.environ["EDITOR"]
    except KeyError as e:
        raise KeyError("Error: EDITOR environment variable needs to be defined", e)


def fetch_directory(date_prefix) -> str | None:
    var_name = "DAILY_NOTES" if date_prefix else "NOTES"
    return os.getenv(var_name) or os.getenv("NOTES") or None


def base_directory(date_prefix):
    slot = "DAILY" if date_prefix else "NOTEBOOK"
    return os.getenv(slot)


def fetch_pager():
    return os.getenv("PAGER")
