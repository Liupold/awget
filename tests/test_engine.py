"""
awget.engine testing module.
"""

import unittest
import os
from time import sleep
from threading import Lock
from awget import engine

URL_LIST = ['http://www.ovh.net/files/1Gb.dat', 'http://speedtest.tele2.net/100MB.zip']
# HASH_LIST = []
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
TMP_DIR = './TmpEngineTest'


class TestHttpEngine(unittest.TestCase):
    """
    Test HttpEngine (/Https).
    """
    @classmethod
    def setUpClass(cls):
        """
        Make the required folders.
        """
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    @classmethod
    def tearDownClass(cls):
        """
        Delete all the tmp files / folders after test.
        """
        if os.path.isdir(TMP_DIR):
            os.rmdir(TMP_DIR)

    def setUp(self):
        """
        Setup the test
        """
        self.dlr = engine.HttpEngine(TEST_URL, TMP_DIR, USER_AGENT)
        self.savefile = os.path.join(TMP_DIR, 'savefile')

    def tearDown(self):
        self.dlr.clean()

    def test_init(self):
        """
        Test for defult and init values.
        """
        self.assertEqual(self.dlr.url, TEST_URL)
        self.assertEqual(self.dlr.max_conn, 8)
        self.assertEqual(self.dlr.max_tries, 10)
        self.assertEqual(self.dlr.agent, USER_AGENT)
        self.assertIsNotNone(self.dlr.session)
        self.assertEqual(self.dlr.session.headers, {'User-Agent': USER_AGENT})
        self.assertEqual(self.dlr.done, 0)
        self.assertIsNone(self.dlr.chunkable)
        self.assertIsNone(self.dlr.size)
        self.assertIsNone(self.dlr.length)
        self.assertEqual(self.dlr.threads, [])
        self.assertIsNone(self.dlr.part_prefix)
        self.assertTrue(isinstance(self.dlr.lock, type(Lock())))

    def test_prepare_chunkable(self):
        """
        Test the prepare methord of HttpEngine
        """
        self.assertEqual(self.dlr.prepare(), True)
        self.assertTrue(isinstance(self.dlr.length, int))
        self.assertTrue(isinstance(self.dlr.chunkable, bool))
        self.assertEqual(self.dlr.done, 0)
        self.assertEqual(len(self.dlr.threads), 8)
        self.assertEqual(self.dlr.is_active(), False)
        self.assertIsNotNone(self.dlr.part_prefix)

    def test_chukable_download(self):
        """
        Test download with no interupt
        """
        self.dlr.download() # should auto prepare.
        self.assertEqual(self.dlr.is_active(), False)
        for part_number in range(self.dlr.max_conn):
            partpath = os.path.join(
                self.dlr.partpath, f'{self.dlr.part_prefix}.{part_number}.part')
            self.assertTrue(os.path.isfile(partpath))
        self.dlr.save(self.savefile)
        # verify hash here
        os.remove(self.savefile)

    def test_chunkable_interupt(self):
        """
        Make sure the file is downloading (atleast).
        """
        self.assertEqual(self.dlr.prepare(), True) # can also be manual.
        self.dlr.download(False)
        self.assertEqual(self.dlr.is_active(), True)
        sleep(3) # download for three second
        self.dlr.stop()
        for part_number in range(self.dlr.max_conn):
            partpath = os.path.join(
                self.dlr.partpath, f'{self.dlr.part_prefix}.{part_number}.part')
            self.assertTrue(os.path.isfile(partpath))

        with self.assertRaises(RuntimeError) as context:
            self.dlr.save(self.savefile)
            self.assertTrue('Download is killed!' in context.exception)

        self.dlr.download() # download what remains. (will auto prepare)
        self.dlr.save(self.savefile)
        self.assertTrue(os.path.isfile(self.savefile))
        os.remove(self.savefile)

if  __name__ == '__main__':
    for TEST_URL in URL_LIST:
        print(TEST_URL)
        unittest.main()
