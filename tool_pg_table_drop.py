#!/usr/bin/python3

import configparser

from lazylib import lazyconfig
from lazylib import lazypg

config = configparser.ConfigParser()
config.read('conf/config.ini')  # everything will be string

pg_instance = lazypg.LazyPg(config)
pg_instance.drop_table()
pg_instance.close()

