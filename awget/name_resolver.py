"""
Resolve name from url/headers/buffer.
"""
from urllib.parse import urlparse
import time
import re
import os
import mimetypes
import magic


def get_extenstion(buff: bytes):
    """
    get the best guess extension from buffer.
    """
    mime_type = magic.from_buffer(buff, mime=True)
    return mimetypes.guess_extension(mime_type)


def get_name_from_headers(headers: dict):
    """
    returns name if possilbe. (else None)
    """
    if 'Content-Disposition' in headers:
        content_disposition = headers['Content-Disposition']
        result = re.search('filename="(.*)"', content_disposition)
        if result is not None:
            return result.group(1)
    return None


def get_name_from_url(url):
    """
    returns the basename of the url.
    """
    fname = os.path.basename(urlparse(url).path)
    if (fname != "") and (len(fname) <= 128):
        return fname
    return None


def improvise_name(url, buff):
    """
    improvise name
    """
    netloc = urlparse(url).netloc
    timestr = time.strftime("%Y-%b-%d-%H.%M.%S")
    ext = get_extenstion(buff)
    return netloc + '_' + timestr + ext


def guess_file_name(url=None, headers=None, buff=None):
    """
    guess file name.
    """
    if headers is not None:
        header_file_name = get_name_from_headers(headers)
        if header_file_name is not None:
            return header_file_name

    if url is not None:
        url_file_name = get_name_from_url(url)
        if url_file_name is not None:
            return url_file_name

    if buff is not None:
        buff_file_name = improvise_name(url, buff)
        if header_file_name is not None:
            return buff_file_name

    return "awget_download-" + time.strftime("%Y-%b-%d-%H.%M.%S")
