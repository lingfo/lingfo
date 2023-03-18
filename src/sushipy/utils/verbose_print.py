from rich import print as rich_print

def verbose_print(message:str, verbose:bool):
    """
    Prints a verbose message using rich library if the 'verbose' flag is set to True.

    Args:
        message (str): The message to be printed.
        verbose (bool): A flag to determine if the message should be printed or not.

    Example:
        verbose_print("This is a verbose message", verbose=True)
    """
    if verbose:
        rich_print(message)
