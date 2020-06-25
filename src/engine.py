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
    def __init__(self, URL:str, PartFileLocation:str, UserAgent: str, \
            MaxConnection=8, MaxTries=10):
        self.url = URL
        self.max_conn = MaxConnection
        self.filepath = FilePath # for part files
        self.agent = UserAgent
        self.session = reqst.Session()
        self.session.headers = {'User-Agent': UserAgent}
        self.done = 0 # done
        self.chunkable = None # Will be initialised later
        self.threads = []
        self.lock = Lock()
        self.__prepared = 0 # Make sure it's prepared.
        self.__killed = False # threads will check this
        self.__part_files = [] #name of all the part files
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
            self.length = False
            self.chunkable = False
        req.close()

        if self.chunk_size is not None:
            # calculate the ramges
            for conn_num in range(self.max_conn):
                upper = self.length - (conn_num * self.chunk_size)
                lower = upper - self.chunk_size + 1
                part_file = os.path.join(self.filepath, \
                        f'{self.part_prefix}.{conn_num}.part')
                self.__part_files.append(part_file)
                if conn_num == (self.max_conn -  1):
                    lower = 0
                self.threads.append(Thread(target=self.__download_chunk, \
                        args=(part_file, (lower, upper)), daemon=True))
        else:
            # download with only one thread!
            part_file = os.path.join(self.filepath, \
                    f'{self.part_prefix}.part')
            self.__part_files.append(part_file)
            self.threads.append(Thread(target=self.__download_chunk, \
                    args=(part_file,), daemon=True))

        self.__part_files.reverse()
        self.__prepared = 1
        return True

    def is_active(self):
        for th in self.threads:
            if th.is_alive():
                return True
        return False

    # this functiom save given chunk into the part file
    # if range is not given download the whole range
    def __download_chunk(self, filepath, int_range_=(None, None)):
        if not None in int_range_:
            lower, upper = int_range_
            range_ = {'Range':f'bytes={lower}-{upper}'}
        else:
            range_ = {}
        req = self.session.get(self.url, headers=range_,stream=True)
        with open(filepath, 'ab+') as f:
            for data in req.iter_content(chunk_size=4096):
                len_ = f.write(data)
                with self.lock:
                    self.done += len_
                    if self.__killed:
                        return 1

    def download(self, block=True):
        if not self.__prepared:
            raise ValueError("Download was never prepared!..")

        self.__killed =  False # Alive again
        for th in self.threads:
            th.start()

        if block:
            for th in self.threads:
                th.join()
            return self.threads
        else:
            return self.threads

    def stop(self):
        if self.is_active:
            self.__killed = True
            for th in self.threads:
                th.join()
            self.__prepared = 0

    def save(self, FilePath):
        if self.is_active():
            raise RuntimeError('Download was active! \
                    Wait for download before calling self.save')
        elif self.__killed:
            raise RuntimeError('Download was killed! \
                    complete the download before calling self.save')
        elif (self.length is not None) and (self.done != self.length):
            raise ValueError('Incomplete Download! \
                    complete the download before calling self.save')
        else:
            w_len = 0
            with open(FilePath, 'wb') as F:
                for part_file in self.__part_files:
                    with open(part_file, 'rb') as f:
                        for data in f:
                            w_len += F.write(data)

    def clean(self):
        if self.is_active():
            self.stop()

        if self.chunk_size is not None:
            for part_file in self.__part_files:
                if os.path.isfile(part_file):
                    os.remove(part_file)

    def __repr__(self):
        return 'awget Engine: ' + str(self.__dict__)


URL = 'https://google.com'
URL = 'http://www.ovh.net/files/1Gb.dat'
FilePath = './Test/'
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

dl = Engine(URL, FilePath, UserAgent)
print(dl.is_active())
dl.prepare()
dl.clean()
dl.download(True)
dl.save('1Gb.dat')
dl.clean()
