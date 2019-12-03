#!/usr/bin/python3

import configparser

from lib import lazyconfig
from lib import lazykafka

config = configparser.ConfigParser()
config.read('conf/config.ini')  # everything will be string
lazyconfig.print_config(config)

kafka_instance = lazykafka.LazyKafka(config)
kafka_instance.delete_topic( config["kafka"]["topic"] )
kafka_instance.close()

