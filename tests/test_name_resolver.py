"""
awget.engine testing module.
author: liupold (rohn chatterjee)
"""

import unittest
import requests
from parameterized import parameterized_class
from awget import name_resolver

URL_LIST = ['https://google.com',
            'http://jell.yfish.us/media/jellyfish-35-mbps-hd-h264.mkv',
            'http://speedtest.tele2.net/100MB.zip',
            'https://speed.hetzner.de/100MB.bin']

@parameterized_class([
    {"url": URL_LIST[0]},
    {"url": URL_LIST[1]},
    {"url": URL_LIST[2]},
    {"url": URL_LIST[3]},
])
class TestChunkableHttpEngine(unittest.TestCase):
    """
    Test HttpEngine (/Https).
    """
    url = ""
    savefile = ""

    def setUp(self):
        self.req = requests.get(self.url, stream=True)
        self.buff = self.req.iter_content(2048).__next__()
        self.req.close()

    def tearDown(self):
        pass

    def test_only_url_guess(self):
        """
        test name_resolver with only url.
        """
        filename = name_resolver.guess_file_name(url=self.url)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'url', filename)

    def test_only_headers_guess(self):
        """
        test name_resolver with only headers
        """
        filename = name_resolver.guess_file_name(headers=self.req.headers)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'headers', filename)

    def test_buff_guess(self):
        """
        test name_resolver with only buffer
        """
        filename = name_resolver.guess_file_name(buff=self.buff)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'buff', filename)

    def test_url_headers_guess(self):
        """
        test name_resolver with url, headers
        """
        filename = name_resolver.guess_file_name(url=self.req.url, \
                headers=self.req.headers)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'url, headers', filename)

    def test_url_buff_guess(self):
        """
        test name_resolver with url, buffer
        """
        filename = name_resolver.guess_file_name(url=self.req.url, \
                buff=self.buff)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'url, buff', filename)

    def test_buff_headers_guess(self):
        """
        test name_resolver with buffer, headers
        """
        filename = name_resolver.guess_file_name(headers=self.req.headers, \
                buff=self.buff)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'url, headers', filename)

    def test_best_guess(self):
        """
        test name_resolver with everything
        """
        filename = name_resolver.guess_file_name(self.req.url, \
                self.req.headers, self.buff)
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'best', filename)

    def test_worst_guess(self):
        """
        test name_resolver with nothing
        """
        filename = name_resolver.guess_file_name()
        self.assertTrue(isinstance(filename, str))
        self.assertTrue(filename != "")
        print('\n', self.url, 'best', filename)

if __name__ == '__main__':
    unittest.main(verbosity=2)
