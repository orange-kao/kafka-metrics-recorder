#!/usr/bin/python3

import configparser
import unittest

from lazylib import lazypg

class TestLazyPg(unittest.TestCase):

    def test_connection(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        pg_instance = lazypg.LazyPg(config)
        pg_instance.close()

    def test_create_table(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        pg_instance = lazypg.LazyPg(config)
        pg_instance.create_table()
        pg_instance.close()

if __name__ == '__main__':
    unittest.main()

