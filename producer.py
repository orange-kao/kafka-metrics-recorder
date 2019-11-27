#!/usr/bin/python3

import configparser
from linux_metrics import cpu_stat
from linux_metrics import disk_stat
from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
import psycopg2

def print_config(config):
    print("Kafka host: %s" % config["kafka"]["host"])
    print("Kafka port: %s" % config["kafka"]["port"])
    print("Kafka CA file: %s" % config["kafka"]["ca_file"])
    print("Kafka cert file: %s" % config["kafka"]["cert_file"])
    print("Kafka key file: %s" % config["kafka"]["key_file"])

    print("Pg host: %s" % config["pg"]["host"])
    print("Pg port: %s" % config["pg"]["port"])
    print("Pg user: %s" % config["pg"]["user"])
    print("Pg password: %s" % config["pg"]["password"])
    print("Pg CA file: %s" % config["pg"]["ca_file"])

def kafka_generate_connection_config(config):
    kafka_config = {}
    # https://kafka-python.readthedocs.io/en/master/apidoc/modules.html
    kafka_config['bootstrap_servers'] = config["kafka"]["host"] + ":" + config["kafka"]["port"]
    kafka_config['security_protocol'] = "SSL"
    kafka_config['ssl_cafile'] = config["kafka"]["ca_file"]
    kafka_config['ssl_certfile'] = config["kafka"]["cert_file"]
    kafka_config['ssl_keyfile'] = config["kafka"]["key_file"]
    return kafka_config

def pg_generate_connection_config(config):
    pg_config = {}
    # https://www.postgresql.org/docs/current/libpq-connect.html
    pg_config["host"] = config["pg"]["host"]
    pg_config["port"] = config["pg"]["port"]
    pg_config['sslmode'] = "verify-full"
    pg_config['sslrootcert'] = config["pg"]["ca_file"]
    pg_config["user"] = config["pg"]["user"]
    pg_config["password"] = config["pg"]["password"]
    pg_config["database"] = config["pg"]["database"]
    return pg_config

config = configparser.ConfigParser()
config.read('config.ini')
print_config(config)

kafka_config = kafka_generate_connection_config(config)
kafka_admin = KafkaAdminClient(**kafka_config)
kafka_producer = KafkaProducer(**kafka_config)
kafka_consumer = KafkaConsumer("topic1", **kafka_config)

pg_config = pg_generate_connection_config(config)
pg_con = psycopg2.connect(**pg_config)

# https://pypi.org/project/linux-metrics/
cpu_util = cpu_stat.cpu_percents(1)
disk_util = disk_stat.disk_usage("/")
cpu_usage = 100 - cpu_util['idle']
disk_usage = disk_util[2] * 100.0 / disk_util[1]
print("CPU usage: %f" % cpu_usage)
print("Disk usage: %f %%" % disk_usage)

topic_list = []
topic_list.append(NewTopic(name="topic1", num_partitions=1, replication_factor=1))
try:
    kafka_admin.create_topics(topic_list)
except TopicAlreadyExistsError:
    print("Topic already exist")

kafka_producer.send("topic1", b"message")

kafka_consumer.topics() # https://github.com/dpkp/kafka-python/issues/601
kafka_consumer.seek_to_beginning()
kafka_consumer.subscribe(['topic1'])


for msg in kafka_consumer:
    print(msg)

