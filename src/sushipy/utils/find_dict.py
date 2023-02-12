"""finds dictonary by value
for example:
    value: "example"
    returns: {"key": "example"}
"""


def find(value, data, key: str):
    """finds dict by value"""

    return next(item for item in data if item[key] == value)
