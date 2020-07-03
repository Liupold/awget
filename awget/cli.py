"""
Basic downloader
"""

from time import sleep
import sys
from awget.engine import HttpEngine
from awget.name_resolver import guess_file_name

URL = sys.argv[1]
# USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
USER_AGENT = 'Wget/1.13.4 (linux-gnu)'
LOCATION = "."


def main():
    """
    Entrypoint. (console_script).
    """
    dlr = HttpEngine(URL, LOCATION, USER_AGENT)
    req = dlr.prepare()
    dlr.download(False)
    while dlr.is_active():
        if dlr.length is not None:
            print(round(dlr.done / dlr.length * 100, 2), end='\r')
        sleep(0.0167)
    dlr.save(guess_file_name(URL, req.headers, req.buff_for_mime))
    dlr.clean()


if __name__ == '__main__':
    main()
