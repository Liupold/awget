"""
Basic downloader
"""

from time import sleep
from engine import HttpEngine

URL = "https://iso.artixlinux.org/iso/artix-base-runit-20200214-x86_64.iso"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
LOCATION = "."

dlr = HttpEngine(URL, LOCATION, USER_AGENT)
dlr.prepare()
dlr.download(False)
while dlr.is_active():
    print(round(dlr.done / dlr.length * 100, 2), end='\r')
    sleep(0.0167)
dlr.save("artix-base-runit-20200214-x86_64.iso")
dlr.clean()
