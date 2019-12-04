#!/usr/bin/python3

import configparser

from lazylib import lazyconfig
from lazylib import lazymetrics
from lazylib import lazykafka
from lazylib import lazypg

config = configparser.ConfigParser()
config.read('conf/config.ini')  # everything will be string

kafka_instance = lazykafka.LazyKafka(config)
kafka_consumer = kafka_instance.create_consumer( config["kafka"]["topic"] )

pg_instance = lazypg.LazyPg(config)
pg_instance.create_table()

kafka_consumer.topics()  # Workaround for kafka-python issue 601
# https://github.com/dpkp/kafka-python/issues/601

kafka_consumer.seek_to_beginning()
kafka_consumer.subscribe([config["kafka"]["topic"]])

for msg in kafka_consumer:
    metrics_dict = lazymetrics.LazyMetrics.bytes_to_dict(msg.value)
    pg_instance.insert_metrics(msg, metrics_dict)
    print( "partition %s, offset %s: %s" %
           (msg.partition, msg.offset, metrics_dict) )

pg_instance.con.close()
kafka_consumer.close()
kafka_instance.close()

