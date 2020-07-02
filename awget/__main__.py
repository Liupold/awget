"""
Basic downloader
"""

from time import sleep
from engine import HttpEngine

URL = "https://github.com/Liupold/awget/archive/master.zip"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
LOCATION = "."

dlr = HttpEngine(URL, LOCATION, USER_AGENT)
print(dlr.max_conn)
dlr.prepare()
dlr.download(False)
while dlr.is_active():
    if dlr.length is not None:
        print(round(dlr.done / dlr.length * 100, 2), end='\r')
    sleep(0.0167)
dlr.save("/dev/null")
dlr.clean()
