from argparse import Action


class JsonFileAction(Action):
    """
    An argparse action that parses a JSON file
    and stores the result in the namespace.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(JsonFileAction, self).__init__(option_strings,
                                             dest,
                                             nargs=nargs,
                                             **kwargs)

    def __call__(self, parser, namespace, file_name: str, option_string=None):
        import json

        try:
            with open(file_name, "r") as f:
                data = json.load(f)
                setattr(namespace, self.dest, data)
        except FileNotFoundError:
            parser.error(f"File {file_name} not found")
