"""
This Module contains the download engine for
`aget` (accelerated wget)

Contains The Following Class:
    * Engine
"""

from threading import Thread, Lock
from hashlib import md5
import os
import base64
import requests as reqst


class HttpEngine():
    """
    Parallel Downloader Engine.
    """
    # pylint: disable=too-many-instance-attributes

    def __init__(self, url: str, partpath: str, useragent: str,
                 MaxConnection=8, MaxTries=10):
        # pylint: disable=too-many-arguments
        self.url = url
        self.max_conn = MaxConnection
        self.max_tries = MaxTries
        self.partpath = partpath  # for part files
        self.agent = useragent
        self.session = reqst.Session()
        self.session.headers = {'User-Agent': useragent}
        self.done = 0  # done
        self.chunkable = None  # Will be initialised later
        self.threads = []
        self.lock = Lock()
        self.__prepared = 0  # Make sure it's prepared.
        self.__killed = False  # threads will check this
        self.__partpaths = []  # name of all the part files
        self.size = None
        self.part_prefix = None
        self.chunk_size = None
        self.length = None

    def prepare(self):
        """
        This prepare the downloader for download
        - This must be ran before downloading
        - or the downloader will run this if not ran by user.
        - this provide more fine control over the download process.
        *this is blocking by nature.*
        returns:
            True after preparation
        """
        self.part_prefix = \
            base64.b64encode(md5(self.url.encode()).
                             digest(), b'..').decode('utf-8')

        req = self.session.get(self.url, stream=True)

        if 'Content-Length' in req.headers:
            self.length = int(req.headers['Content-Length'])
            self.chunkable = 'Accept-Ranges' in req.headers
            if self.chunkable:
                self.chunk_size = self.length // self.max_conn
        else:
            self.length = None
            self.chunkable = False
        req.close()

        if self.chunk_size is not None:
            # calculate the ranges
            for part_number in range(self.max_conn):
                upper = self.length - (part_number * self.chunk_size)
                lower = upper - self.chunk_size + 1
                partpath = os.path.join(
                    self.partpath, f'{self.part_prefix}.{part_number}.part')
                self.__partpaths.append(partpath)
                if part_number == (self.max_conn - 1):
                    lower = 0
                # resume
                if os.path.isfile(partpath):
                    file_length = os.path.getsize(partpath)
                    if file_length < (upper - lower):
                        lower += file_length
                        self.done += file_length
                    elif file_length in (upper - lower + 1, upper - lower):
                        # this means the part is completed
                        self.done += file_length
                        continue  # do not append to self.threads
                    else:
                        raise RuntimeError("File Corrupted!")
                self.threads.append(
                    Thread(
                        target=self.__download_chunk, args=(
                            partpath, (lower, upper)), daemon=True))
        else:
            # download with only one thread!
            partpath = os.path.join(self.partpath,
                                    f'{self.part_prefix}.part')
            self.__partpaths.append(partpath)
            self.threads.append(Thread(target=self.__download_chunk,
                                       args=(partpath,), daemon=True))

        # this is done as the threads are reverse in order.
        self.__partpaths.reverse()
        self.__prepared = 1
        return True

    def is_active(self):
        """
        Returns a *bool*:
            Indicating if downloader is running or not.
            can be called at any ponit.
        """
        for thread_ in self.threads:
            if thread_.is_alive():
                return True
        return False

    def __download_chunk(self, partpath, int_range_=(None, None)):
        """
        this function save given chunk into the part file
        if range is not given download from beginning to the end.
        """
        if None not in int_range_:
            lower, upper = int_range_
            range_ = {'Range': f'bytes={lower}-{upper}'}
            print(range_)
        else:
            range_ = {}
        req = self.session.get(self.url, headers=range_, stream=True)
        with open(partpath, 'ab+') as partfile:
            for data in req.iter_content(chunk_size=4096):
                len_ = partfile.write(data)
                with self.lock:
                    self.done += len_
                    if self.__killed:
                        return 1
        return 0

    def download(self, block=True):
        """
        This downloads the given URL.
        Takes a bool which indicates the blocking status of the downloaded:
           True: block till finished (or killed)
           False: run in background
        Returns a list of threads.
        """
        if not self.__prepared:
            self.prepare()

        self.__killed = False  # Alive again
        for thread_ in self.threads:
            thread_.start()

        if block:
            self.join()

        return self.threads

    def join(self):
        """
        join all the thread with the main thread.
        (wait for the download to finish).
        """
        for thread_ in self.threads:
            thread_.join()

    def stop(self):
        """
        Stop the download process.
        """
        if self.is_active():
            self.__killed = True
            self.join()
            self.__prepared = 0

    def save(self, filename):
        """
        Save the downloaded file to a given path.
        Must be called after download is finished.
        """
        if self.is_active():
            raise RuntimeError('Download was active! \
                    Wait for download before calling self.save')
        if self.__killed:
            raise RuntimeError('Download was killed! \
                    complete the download before calling self.save')
        if (self.length is not None) and (self.done != self.length):
            print(self.done, self.length)
            raise ValueError('Incomplete Download! \
                    complete the download before calling self.save')
        bytes_written = 0
        with open(filename, 'wb') as finalfile:
            for partpath in self.__partpaths:
                with open(partpath, 'rb') as partfile:
                    for data in partfile:
                        bytes_written += finalfile.write(data)

    def clean(self):
        """
        remove all the part files.
        """
        if self.is_active():
            self.stop()

        if self.chunk_size is not None:
            for partpath in self.__partpaths:
                if os.path.isfile(partpath):
                    os.remove(partpath)

    def __repr__(self):
        return 'awget Engine: ' + str(self.__dict__)


URL = 'https://google.com'
URL = 'https://speed.hetzner.de/100MB.bin'
TMP_PATH = './Test/'
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

dl = HttpEngine(URL, TMP_PATH, USER_AGENT)
print(dl.is_active())
# dl.prepare()
dl.clean()
dl.download(True)
dl.save('100MB.bin')
# dl.clean()
