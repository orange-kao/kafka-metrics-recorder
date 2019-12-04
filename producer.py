#!/usr/bin/python3

import configparser

from lazylib import lazyconfig
from lazylib import lazymetrics
from lazylib import lazykafka

config = configparser.ConfigParser()
config.read('conf/config.ini')  # everything will be string

kafka_instance = lazykafka.LazyKafka(config)
kafka_instance.create_topic( config["kafka"]["topic"] )

kafka_producer = kafka_instance.create_producer()
metrics_instance = lazymetrics.LazyMetrics(config)

while True:
    metrics_json_bytes = metrics_instance.get_bytes()
    kafka_producer.send(config["kafka"]["topic"], metrics_json_bytes)
    kafka_producer.flush()
    print("Push to Kafka: %s" % (metrics_json_bytes,))

kafka_producer.close()
kafka_instance.close()

