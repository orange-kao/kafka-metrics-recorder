#!/usr/bin/python3

import configparser
import json

from kafka import KafkaConsumer
import psycopg2

import lazyconfig
import lazymetrics
import lazykafka
import lazypg

config = configparser.ConfigParser()
config.read('config.ini')  # everything will be string
lazyconfig.print_config(config)

kafka_instance = lazykafka.LazyKafka(config)
kafka_consumer = kafka_instance.create_consumer( config["kafka"]["topic"] )

pg_instance = lazypg.LazyPg(config)
#pg_instance.drop_table()
pg_instance.create_table()
pg_instance.con.commit()
pg_instance.con.close()

kafka_consumer.topics()  # Workaround for kafka-python issue 601
# https://github.com/dpkp/kafka-python/issues/601

kafka_consumer.seek_to_beginning()
kafka_consumer.subscribe([config["kafka"]["topic"]])

for msg in kafka_consumer:
#    print(json.loads(msg.value.decode()))
    print(lazymetrics.LazyMetrics.bytes_to_dict(msg.value))

kafka_consumer.close()

