#!/usr/bin/python3

import configparser
import unittest

from lazylib import lazykafka

class TestLazyKafka(unittest.TestCase):

    def test_connection(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        kafka_instance = lazykafka.LazyKafka(config)
        kafka_instance.close()

    def test_create_topic(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        kafka_instance = lazykafka.LazyKafka(config)
        kafka_instance.create_topic( config["kafka"]["topic"] )
        kafka_instance.close()

    def test_create_producer_and_consumer(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        kafka_instance = lazykafka.LazyKafka(config)
        kafka_producer = kafka_instance.create_producer()
        kafka_consumer = kafka_instance.create_consumer( config["kafka"]["topic"] )

        kafka_producer.close()
        kafka_consumer.close()
        kafka_instance.close()

if __name__ == '__main__':
    unittest.main()

