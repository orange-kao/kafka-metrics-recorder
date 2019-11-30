#!/usr/bin/python3

import configparser
import socket
import time

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
    print("Kafka topic: %s" % config["kafka"]["topic"])

    print("Pg host: %s" % config["pg"]["host"])
    print("Pg port: %s" % config["pg"]["port"])
    print("Pg user: %s" % config["pg"]["user"])
    print("Pg password: %s" % config["pg"]["password"])
    print("Pg CA file: %s" % config["pg"]["ca_file"])

def kafka_generate_connection_config(config):
    kafka_config = {}
    # https://kafka-python.readthedocs.io/en/master/apidoc/modules.html
    kafka_config['bootstrap_servers'] = config["kafka"]["host"] + \
                                        ":" + config["kafka"]["port"]
    kafka_config['security_protocol'] = "SSL"
    kafka_config['ssl_cafile'] = config["kafka"]["ca_file"]
    kafka_config['ssl_certfile'] = config["kafka"]["cert_file"]
    kafka_config['ssl_keyfile'] = config["kafka"]["key_file"]

    # At least
    #   * specify api_version - won't work without pull-request
    #       https://github.com/dpkp/kafka-python/pull/1953
    #   OR
    #   * specify api_version_auto_timeout_ms
    #       with a large enough value (2000 ms default may not enough)
    # Otherwise kafka.errors.NoBrokersAvailable exception is possible
    # under high latency link

    # Specify api_version_auto_timeout_ms need to be increased because
    #   * It use fixed timeout for API version test, does not take TCP
    #     3-way handshak and TLS establishment time into account, and
    #     does not aware the TCP segment is still being transmitted
    #     (ongoing connection), thus doesn't adapt high latency
    #      connection well
    #   * Bug in the library, 1074 ms from TCP SYN (first message of TCP
    #     3-way handshaking) to FIN (cutting connection), which is less
    #     than 2000 ms

    # Sniff looks like this
    # Time         Src            Dst            Proto    Info
    # 0.000000000  10.0.0.1       35.201.23.103  TCP      [SYN]
    # 0.608208866  35.201.23.103       10.0.0.1  TCP      [SYN, ACK]
    # 0.608236387  10.0.0.1       35.201.23.103  TCP      [ACK]
    # 0.610008710  10.0.0.1       35.201.23.103  TLSv1.2  Client Hello
    # 1.074809881  10.0.0.1       35.201.23.103  TCP      [FIN, ACK]
    # 1.208294982  35.201.23.103       10.0.0.1  TCP      [ACK]
    # 1.237219542  35.201.23.103       10.0.0.1  TCP      [ACK]
    # 1.237261544  10.0.0.1       35.201.23.103  TCP      [RST]
    # 1.237445431  35.201.23.103       10.0.0.1  TCP      [ACK]
    # 1.237459685  10.0.0.1       35.201.23.103  TCP      [RST]
    # 1.249931364  35.201.23.103       10.0.0.1  TLSv1.2  Server Hello,
    #                                              Certificate,
    #                                              Server Key Exchange,
    #                                              Certificate Request,
    #                                              Server Hello Done
    # 1.249971500  10.0.0.1       35.201.23.103  TCP      [RST]
    # 1.439006072  35.201.23.103       10.0.0.1  TCP      [FIN, ACK]
    # 1.439029718  10.0.0.1       35.201.23.103  TCP      [RST]

#    kafka_config['api_version'] = (1,0,0)
    # not work on kafka-python 1.4.7 unless PR 1953 has been accepted
    # https://github.com/dpkp/kafka-python/pull/1953


    kafka_config['api_version_auto_timeout_ms'] = 10_000
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

def kafka_create_topic(kafka_config, config):
    kafka_admin = KafkaAdminClient(**kafka_config)
    topic_list = []
    topic_list.append(NewTopic( name=config["kafka"]["topic"],
                                num_partitions=1, replication_factor=1 ))
    try:
        kafka_admin.create_topics(topic_list)
        print("Topic created successfully")
    except TopicAlreadyExistsError:
        print("Topic already exist")

def pg_drop_table(pg_cur):
    drop_table_sql = """
    drop table if exists machine_metrics;
    """

    pg_cur.execute(drop_table_sql)

def pg_create_table(pg_cur):
    # hostname 63 char max. FQDN 253 char max
    # http://man7.org/linux/man-pages/man7/hostname.7.html

    # Postgres date type 'integer' as epoch date:
    #       up to 2147483647,
    #       which will be problemmatic in A.D. 2038
    # Postgres date type 'bigint' as epoch date:
    #       up to 9223372036854775807,
    #       which will be problemmatic in A.D. 292277026596
    # Postgres date type 'timestamp':
    #       4713 BC to 294276 AD, 1 microsecond resolution

    # Postgres date type 'real': IEEE 754 single precision
    # https://www.postgresql.org/docs/current/datatype-numeric.html

    create_table_sql = """
    create table machine_metrics(
        hostname varchar(253) not null,
        time timestamp not null,
        cpu_usage real not null,
        disk_usage real not null
    );
    """

    try:
        pg_cur.execute(create_table_sql)
        print("Table created successfully")
    except psycopg2.errors.DuplicateTable:
        print("Table already exist")

def metric_collect():
    hostname = socket.gethostname()
    time_epoch = int(time.time())

    # https://pypi.org/project/linux-metrics/
    cpu_util = cpu_stat.cpu_percents(1)
    disk_util = disk_stat.disk_usage("/")
    cpu_usage = 100 - cpu_util['idle']
    disk_usage = disk_util[2] * 100.0 / disk_util[1]

    print("CPU usage: %f" % cpu_usage)
    print("Disk usage: %f %%" % disk_usage)
    return {"hostname":hostname,
            "cpu_usage":cpu_usage,
            "disk_usage":disk_usage}


config = configparser.ConfigParser()
config.read('config.ini')
print_config(config)

kafka_config = kafka_generate_connection_config(config)
kafka_create_topic(kafka_config, config)
kafka_producer = KafkaProducer(**kafka_config)
kafka_consumer = KafkaConsumer(config["kafka"]["topic"], **kafka_config)

pg_config = pg_generate_connection_config(config)
pg_con = psycopg2.connect(**pg_config)
pg_cur = pg_con.cursor()
pg_drop_table(pg_cur)
pg_create_table(pg_cur)
pg_cur.close()
print(type(pg_con))
pg_con.commit()
pg_con.close()

#metric_collect()


kafka_producer.send(config["kafka"]["topic"], b"message")
kafka_producer.flush()

kafka_consumer.topics()  # Workaround for kafka-python issue 601
# https://github.com/dpkp/kafka-python/issues/601

kafka_consumer.seek_to_beginning()
kafka_consumer.subscribe([config["kafka"]["topic"]])

for msg in kafka_consumer:
    print(msg)

kafka_producer.close()
kafka_consumer.close()

