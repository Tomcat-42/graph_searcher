def read_json_file(file_name: str):
    """
    Read a JSON file and return the contents as a string.
    """
    import json

    try:
        with open(file_name, "r") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        raise FileNotFoundError(f"File {file_name} not found")
