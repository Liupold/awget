"""
Common (non specific) small fuctions goes here (for awget)
"""
import io


def open_file(file_):
    """
    if file_ is <file object> : returs file_
    if file_ is str: opens the file and resturns the file object.
    """
    if isinstance(file_, io.BufferedIOBase):
        return file_
    if isinstance(file_, str):
        return open(file_, 'ab+')
    raise ValueError(f"Unable to understand file: {file_}")
