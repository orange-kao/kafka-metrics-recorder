#!/usr/bin/python3

import configparser

from lazylib import lazyconfig
from lazylib import lazykafka

config = configparser.ConfigParser()
config.read('conf/config.ini')  # everything will be string

kafka_instance = lazykafka.LazyKafka(config)
kafka_instance.delete_topic( config["kafka"]["topic"] )
kafka_instance.close()

