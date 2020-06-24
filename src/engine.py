import requests as reqst
from multiprocessing import Pool
from threading import Thread, Lock
from hashlib import md5; import base64
import os

class Engine():
    """
    Parallel Downloader Engine.
    """
    def __init__(self, URL:str, PartFileLocation:str, UserAgent: str, \
            MaxConnection=8, MaxTries=10):
        self.url = URL
        self.max_conn = MaxConnection
        self.filepath = FilePath # for part files
        self.agent = UserAgent
        self.session = reqst.Session()
        self.session.headers = {'User-Agent': UserAgent}
        self.__process = [] # get requests
        self.__prepared = 0 # Make sure it's prepared.
        self.done = 0 # done
        self.chunkable = None # Will be initialised later
        self.threads = []
        self.lock = Lock()
        self.killed = False # threads will check this
        self.size = None
        self.chunk_size = None

    def Prepare(self):
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

        self.part_prefix = \
                base64.b64encode(md5(self.url.encode()).\
                digest(), b'..').decode('utf-8')
        self.__prepared = 1
        return True

    def Download(self, block=True):

        def download_chunk(filepath, lower, upper):
                range_ = {'Range':f'bytes={lower}-{upper}'}
                req = self.session.get(self.url, headers=range_,stream=True)
                with open(filepath, 'ab+') as f:
                    for data in req.iter_content(chunk_size=4096):
                        len_ = f.write(data)
                        with self.lock: self.done += len_
                    if self.killed: return 1

        if self.chunk_size is not None:
            for conn_num in range(self.max_conn - 1):
                upper = self.length - conn_num * self.chunk_size
                lower = upper - self.chunk_size + 1
                part_file = os.path.join(self.filepath, \
                        f'{self.part_prefix}.{conn_num}.part')
                self.threads.append(Thread(target=download_chunk, \
                        args=(part_file, lower, upper), daemon=True))

            upper = lower - 1; lower = 0
            self.threads.append(Thread(target=download_chunk, \
                    args=(part_file, lower, upper), daemon=True))
            [ th.start() for th in self.threads ]
            if block:
                return [ th.join() for th in self.threads ]
            else:
                return self.threads

    def SaveFile(self, FinalFilePath):
        pass


    def __repr__(self):
        return 'awget Engine: ' + str(self.__dict__)


URL = 'http://www.ovh.net/files/1Gb.dat'
FilePath = '.'
UserAgent = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'

dl = Engine(URL, FilePath, UserAgent)
dl.Prepare()
print(dl.Download())
