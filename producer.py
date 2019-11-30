#!/usr/bin/python3

import configparser
import json

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import psycopg2

import lazykafka
import lazypg
import lazymetrics
import lazyconfig

config = configparser.ConfigParser()
config.read('config.ini')  # everything will be string
lazyconfig.print_config(config)

kafka_config = lazykafka.generate_connection_config(config)
#lazykafka.delete_topic( kafka_config=kafka_config,
#                        topic=config["kafka"]["topic"] )
lazykafka.create_topic( kafka_config=kafka_config,
                        topic=config["kafka"]["topic"] )
kafka_producer = KafkaProducer(**kafka_config)

metrics_dict = lazymetrics.collect(config)
metrics_json_bytes = json.dumps(metrics_dict).encode()

kafka_producer.send(config["kafka"]["topic"], metrics_json_bytes)
kafka_producer.flush()

kafka_producer.close()

