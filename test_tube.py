"""
This file is only for experiments
"""
from time import sleep
from awget.engine import HttpEngine
import magic

URL = "https://www.dropbox.com/s/mx2n1d4ejdtifzg/Feelin%27%20Good.mp3?dl=0"
#USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
USER_AGENT = 'Wget/1.13.4 (linux-gnu)'
LOCATION = "."

dlr = HttpEngine(URL, LOCATION, USER_AGENT)
print(dlr.max_conn)
print(dlr.prepare())
dlr.download(False)
while dlr.is_active():
    if dlr.length is not None:
        print(round(dlr.done / dlr.length * 100, 2), end='\r')
    sleep(0.0167)
dlr.save("test.mp3")
dlr.clean()
