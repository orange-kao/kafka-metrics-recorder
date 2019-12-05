#!/usr/bin/python3

def print_config(config):
    print( f"Kafka host: {config['kafka']['host']}" )
    print( f"Kafka port: {config['kafka']['port']}" )
    print( f"Kafka CA file: {config['kafka']['ca_file']}" )
    print( f"Kafka cert file: {config['kafka']['cert_file']}" )
    print( f"Kafka key file: {config['kafka']['key_file']}" )
    print( f"Kafka topic: {config['kafka']['topic']}" )

    print( f"Pg host: {config['pg']['host']}" )
    print( f"Pg port: {config['pg']['port']}" )
    print( f"Pg user: {config['pg']['user']}" )
    print( f"Pg password: {config['pg']['password']}" )
    print( f"Pg CA file: {config['pg']['ca_file']}" )

