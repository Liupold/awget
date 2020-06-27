"""
awget.engine testing module.
"""

import unittest
import os
import filecmp
from time import sleep
from threading import Lock
from parameterized import parameterized_class
from awget import engine

URL_LIST = ['http://www.ovh.net/files/1Gb.dat',
            'http://speedtest.tele2.net/100MB.zip',
            'https://speed.hetzner.de/100MB.bin']
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; rv:68.0) Gecko/20100101 Firefox/68.0'
TMP_DIR = 'tmp-for-awget'


@parameterized_class([
    {"url": URL_LIST[0], "savefile": os.path.join(TMP_DIR, '1Gb.dat')},
    {"url": URL_LIST[1], "savefile": os.path.join(TMP_DIR, '100MB.zip')},
    {"url": URL_LIST[2], "savefile": os.path.join(TMP_DIR, '100MB.bin')},
])
class TestChunkableHttpEngine(unittest.TestCase):
    """
    Test HttpEngine (/Https).
    """
    url = ""
    savefile = ""

    @classmethod
    def setUpClass(cls):
        """
        Make the required folders.
        """
        print(f"Testing with url:[{cls.url}]({cls.savefile})")
        if not os.path.isdir(TMP_DIR):
            os.mkdir(TMP_DIR)

    @classmethod
    def tearDownClass(cls):
        """
        Delete all the tmp files / folders after test.
        """
        return 0

    def setUp(self):
        """
        Setup the test
        """
        self.dlr = engine.HttpEngine(self.url, TMP_DIR, USER_AGENT)

    def tearDown(self):
        self.dlr.clean()  # can be called just after __init__ (without prepare)

    def test_init(self):
        """
        Test for default and init values.
        """
        self.assertEqual(self.dlr.url, self.url)
        self.assertEqual(self.dlr.max_conn, 8)
        self.assertEqual(self.dlr.max_retries, 10)
        self.assertEqual(self.dlr.agent, USER_AGENT)
        self.assertIsNotNone(self.dlr.session)
        self.assertEqual(self.dlr.session.headers, {'User-Agent': USER_AGENT})
        self.assertEqual(self.dlr.done, 0)
        self.assertIsNone(self.dlr.chunkable)
        self.assertIsNone(self.dlr.length)
        self.assertIsNone(self.dlr.chunk_size)
        self.assertEqual(self.dlr.threads, [])
        self.assertIsNone(self.dlr.part_prefix)
        self.assertTrue(isinstance(self.dlr.lock, type(Lock())))

    def test_prepare_chunkable(self):
        """
        Test the prepare method of HttpEngine
        """
        self.assertEqual(self.dlr.prepare(), True)
        self.assertTrue(isinstance(self.dlr.length, int))
        self.assertTrue(isinstance(self.dlr.chunk_size, int))
        self.assertTrue(self.dlr.chunkable)
        self.assertEqual(self.dlr.done, 0)
        self.assertTrue(isinstance(self.dlr.threads, list))
        self.assertEqual(len(self.dlr.threads), 8)
        self.assertEqual(self.dlr.is_active(), False)
        self.assertIsNotNone(self.dlr.part_prefix)

    def test_chukable_download(self):
        """
        Test download with no interrupt
        """
        self.dlr.download()  # should auto prepare.
        self.assertEqual(self.dlr.is_active(), False)
        for part_number in range(self.dlr.max_conn):
            partpath = os.path.join(
                self.dlr.partpath, f'{self.dlr.part_prefix}.{part_number}.part')
            self.assertTrue(os.path.isfile(partpath))
        self.dlr.save(self.savefile + ".no_interrupt")
        self.assertTrue(os.path.isfile(self.savefile + ".no_interrupt"))
        self.assertTrue(filecmp.cmp(self.savefile + ".no_interrupt",
                                    self.savefile + ".curl"))
        os.remove(self.savefile + ".no_interrupt")

    def test_chunkable_interupt(self):
        """
        interrupt test (resume test). (also test for over downloading).
        """
        self.assertTrue(self.dlr.prepare())  # can also be manual.
        self.dlr.download(False)
        sleep(1)
        self.dlr.stop()

        for part_number in range(self.dlr.max_conn):
            partpath = os.path.join(
                self.dlr.partpath, f'{self.dlr.part_prefix}.{part_number}.part')
            self.assertTrue(os.path.isfile(partpath))

        with self.assertRaises(RuntimeError) as context:
            self.dlr.save(self.savefile + ".interrupt")
            self.assertFalse(os.path.isfile(self.savefile + ".interrupt"))
            self.assertTrue('Download is killed!' in context.exception)

        for _ in range(10):
            self.dlr.download(False)
            sleep(1)  # download for some time
            self.dlr.stop()
            self.assertFalse(self.dlr.is_active())

        self.dlr.download()  # download what remains. (will auto prepare)
        self.dlr.save(self.savefile + ".interrupt")
        self.assertTrue(os.path.isfile(self.savefile + ".interrupt"))
        self.assertTrue(filecmp.cmp(self.savefile + ".interrupt",
                                    self.savefile + ".curl"))
        os.remove(self.savefile + ".interrupt")

    def test_custom_split(self):
        """
        Specific numbers of download threads. max_conn=(1, 20)
        """
        self.dlr = engine.HttpEngine(self.url, TMP_DIR, USER_AGENT, 1)
        self.test_chukable_download()
        self.dlr.clean()
        self.dlr = engine.HttpEngine(self.url, TMP_DIR, USER_AGENT, 20)
        self.dlr.clean()


if __name__ == '__main__':
    unittest.main(verbosity=2)
