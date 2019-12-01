#!/usr/bin/python3

import configparser

from kafka import KafkaProducer

import lazyconfig
import lazymetrics
import lazykafka

config = configparser.ConfigParser()
config.read('config.ini')  # everything will be string
lazyconfig.print_config(config)

kafka_instance = lazykafka.LazyKafka(config)
#kafka_instance.delete_topic( config["kafka"]["topic"] )
kafka_instance.create_topic( config["kafka"]["topic"] )
kafka_producer = kafka_instance.create_producer()

metrics_instance = lazymetrics.LazyMetrics(config)
metrics_json_bytes = metrics_instance.get_bytes()

kafka_producer.send(config["kafka"]["topic"], metrics_json_bytes)
kafka_producer.flush()

kafka_producer.close()

