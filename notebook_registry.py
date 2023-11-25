from notebook import Notebook


class NotebookRegistry:
    @property
    @classmethod
    def current(cls):
        """Gets the currently active notebook."""
        with open("/Users/nick/.notebooks") as f:
            directory = f.readline().rstrip("\n")
        return Notebook(directory)

    @current.setter
    @classmethod
    def current(cls, notebook):
        """Sets the currently active notebook."""
        with open("/Users/nick/.notebooks", "r") as file:
            lines = file.readlines()
        with open("/Users/nick/.notebooks", "w") as file:
            file.write(notebook.directory)
            for line in lines:
                if not line.startswith(notebook.directory):
                    file.write(line)

    @classmethod
    def list(cls):
        """Lists all available notebooks of the user"""
        with open("/Users/nick/.notebooks") as f:
            return f.read().strip("\n")
