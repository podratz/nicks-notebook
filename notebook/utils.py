import os


class UnsupportedEditorException(Exception):
    def __init__(self, editor: str):
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


def fetch_base_directory(is_dated_note: bool) -> str:
    var_name = "DAILY_NOTES" if is_dated_note else "NOTES"
    base = os.getenv(var_name) or os.getenv("NOTES")
    if not base:
        raise EnvironmentError("Could not fetch base directory")
    return base


def base_directory(date_prefix: str) -> str | None:
    slot = "DAILY" if date_prefix else "NOTEBOOK"
    return os.getenv(slot)


def fetch_pager() -> str | None:
    return os.getenv("PAGER")
