import requests as reqst
from multiprocessing import Pool
from threading import Thread, Lock
from hashlib import md5; import base64
import os

from time import sleep

class Engine():
    """
    Para Downloader Engine.
    """
    def __init__(self, URL:str, PartFilePath:str, UserAgent: str, \
            MaxConnection=8, MaxTries=10):
        self.url = URL
        self.max_conn = MaxConnection
        self.partpath = PartFilePath # for part files
        self.agent = UserAgent
        self.session = reqst.Session()
        self.session.headers = {'User-Agent': UserAgent}
        self.done = 0 # done
        self.chunkable = None # Will be initialised later
        self.threads = []
        self.lock = Lock()
        self.__prepared = 0 # Make sure it's prepared.
        self.__killed = False # threads will check this
        self.__partpaths = [] #name of all the part files
        self.size = None
        self.chunk_size = None


    def prepare(self):
        self.part_prefix = \
                base64.b64encode(md5(self.url.encode()).\
                digest(), b'..').decode('utf-8')

        req = self.session.get(self.url, stream=True)
        if 'Content-Length' in req.headers:
            self.length = int(req.headers['Content-Length'])
            self.chunkable = True if 'Accept-Ranges' in req.headers else False
            if self.chunkable:
                self.chunk_size = self.length // self.max_conn
        else:
            self.length = None
            self.chunkable = False
        req.close()

        if self.chunk_size is not None:
            # calculate the ramges
            for conn_num in range(self.max_conn):
                upper = self.length - (conn_num * self.chunk_size)
                lower = upper - self.chunk_size + 1
                partpath = os.path.join(self.partpath, \
                        f'{self.part_prefix}.{conn_num}.part')
                self.__partpaths.append(partpath)
                if conn_num == (self.max_conn -  1):
                    lower = 0
                # resume
                if os.path.isfile(partpath):
                    file_length = os.path.getsize(partpath)
                    if file_length < (upper - lower):
                        lower += file_length
                        self.done += file_length
                    elif (file_length == upper - lower + 1) or \
                            (file_length == upper - lower):
                        # this means the part is completed
                        self.done += file_length
                        continue # do not append to thread
                    else:
                        raise RuntimeError("File Corrupted!")
                self.threads.append(Thread(target=self.__download_chunk, \
                        args=(partpath, (lower, upper)), daemon=True))
        else:
            # download with only one thread!
            partpath = os.path.join(self.partpath, \
                    f'{self.part_prefix}.part')
            self.__partpaths.append(partpath)
            self.threads.append(Thread(target=self.__download_chunk, \
                    args=(partpath,), daemon=True))

        self.__partpaths.reverse()
        self.__prepared = 1
        return True


    def is_active(self):
        for th in self.threads:
            if th.is_alive():
                return True
        return False

    # this function save given chunk into the part file
    # if range is not given download the whole range
    def __download_chunk(self, partpath, int_range_=(None, None)):
        if not None in int_range_:
            lower, upper = int_range_
            range_ = {'Range':f'bytes={lower}-{upper}'}
            print(range_)
        else:
            range_ = {}
        req = self.session.get(self.url, headers=range_, stream=True)
        with open(partpath, 'ab+') as f:
            for data in req.iter_content(chunk_size=4096):
                len_ = f.write(data)
                with self.lock:
                    self.done += len_
                    if self.__killed: return 1


    def download(self, block=True):
        if not self.__prepared:
            self.prepare()

        self.__killed =  False # Alive again
        for th in self.threads:
            th.start()

        if block:
            self.join()
            return self.threads
        else:
            return self.threads

    def join(self):
        for th in self.threads:
            th.join()

    def stop(self):
        if self.is_active():
            self.__killed = True
            self.join()
            self.__prepared = 0


    def save(self, FilePath):
        if self.is_active():
            raise RuntimeError('Download was active! \
                    Wait for download before calling self.save')
        elif self.__killed:
            raise RuntimeError('Download was killed! \
                    complete the download before calling self.save')
        elif (self.length is not None) and (self.done != self.length):
            print(self.done, self.length)
            raise ValueError('Incomplete Download! \
                    complete the download before calling self.save')
        else:
            w_len = 0
            with open(FilePath, 'wb') as F:
                for partpath in self.__partpaths:
                    with open(partpath, 'rb') as f:
                        for data in f: w_len += F.write(data)

    def clean(self):
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
tmpPath = './Test/'
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

dl = Engine(URL, tmpPath, UserAgent)
print(dl.is_active())
# dl.prepare()
dl.clean()
dl.download(True)
dl.save('100MB.bin')
# dl.clean()
