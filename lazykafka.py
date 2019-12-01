#!/usr/bin/python3

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError
from kafka.errors import UnknownTopicOrPartitionError

class LazyKafka:
    def __init__(self, config):
        self.config = config["kafka"]
        self.kafka_config = self.generate_connection_config(config["kafka"])

    @staticmethod
    def generate_connection_config(config):
        kafka_config = {}
        # https://kafka-python.readthedocs.io/en/master/apidoc/modules.html
        kafka_config['bootstrap_servers'] = config["host"] + \
                                            ":" + config["port"]
        kafka_config['security_protocol'] = "SSL"
        kafka_config['ssl_cafile'] = config["ca_file"]
        kafka_config['ssl_certfile'] = config["cert_file"]
        kafka_config['ssl_keyfile'] = config["key_file"]

        # At least specify one of the following
        #   * api_version - won't work without pull-request
        #       https://github.com/dpkp/kafka-python/pull/1953
        #   * api_version_auto_timeout_ms
        #       with a large enough value (2000 ms default may not enough)
        # Otherwise kafka.errors.NoBrokersAvailable exception is possible
        # under high latency network connection

        # Specify api_version_auto_timeout_ms need to be increased because
        #   * It use fixed timeout for API version test, does not take TCP
        #     3-way handshak and TLS establishment time into account, and
        #     does not aware the TCP segment is still being transmitted
        #     (ongoing connection), thus doesn't adapt high latency
        #     connection well
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

        # kafka_config['api_version'] = (1,0,0)
        # not work on kafka-python 1.4.7 unless PR 1953 has been accepted
        # https://github.com/dpkp/kafka-python/pull/1953

        kafka_config['api_version_auto_timeout_ms'] = 10_000
        return kafka_config

    def delete_topic(self, topic):
        kafka_admin = KafkaAdminClient(**self.kafka_config)
        try:
            kafka_admin.delete_topics([topic])
            print("Topic deleted successfully")
        except UnknownTopicOrPartitionError:
            print("Topic does not exist")

    def create_topic(self, topic):
        kafka_admin = KafkaAdminClient(**self.kafka_config)
        topic_list = []
        topic_list.append(NewTopic(
            name=topic,
            num_partitions=int(self.config["num_partitions"]),
            replication_factor=int(self.config["replication_factor"])
            ))
        try:
            kafka_admin.create_topics(topic_list)
            print("Topic created successfully")
        except TopicAlreadyExistsError:
            print("Topic already exist")

    def create_producer(self):
        producer = KafkaProducer(**self.kafka_config)
        return producer

    def create_consumer(self, topics):
        consumer = KafkaConsumer(topics, **self.kafka_config)
        return consumer

