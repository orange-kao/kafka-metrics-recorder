#!/usr/bin/python3

import configparser

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

