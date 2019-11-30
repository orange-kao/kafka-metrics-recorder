#!/usr/bin/python3

import psycopg2

def generate_connection_config(config):
    # http://initd.org/psycopg/docs/module.html

    # Documentation for sslmode
    # https://www.postgresql.org/docs/current/libpq-connect.html

    pg_config = {}
    pg_config["host"] = config["pg"]["host"]
    pg_config["port"] = config["pg"]["port"]
    pg_config['sslmode'] = "verify-full"
    pg_config['sslrootcert'] = config["pg"]["ca_file"]
    pg_config["user"] = config["pg"]["user"]
    pg_config["password"] = config["pg"]["password"]
    pg_config["dbname"] = config["pg"]["database"]
    return pg_config

def drop_table(pg_con):
    drop_table_sql = """
        drop table if exists metrics;
        drop table if exists machine;
        """
    pg_cur = pg_con.cursor()
    pg_cur.execute(drop_table_sql)
    pg_cur.close()

def create_table(pg_con):
    # Linux hostname is 63 char max. FQDN 253 char max
    # http://man7.org/linux/man-pages/man7/hostname.7.html

    # Postgres date type 'integer' as epoch date:
    #       up to 2147483647,
    #       which will be problemmatic in A.D. 2038
    # Postgres date type 'bigint' as epoch date:
    #       up to 9223372036854775807,
    #       which will be problemmatic in A.D. 292277026596
    # Postgres date type 'timestamp':
    #       4713 BC to 294276 AD, 1 microsecond resolution

    # Postgres date type 'integer' as epoch date:
    #       up to 2147483647,
    #       which will be problemmatic in A.D. 2038

    # Postgres date type 'real': IEEE 754 single precision
    # https://www.postgresql.org/docs/current/datatype-numeric.html

    create_table_sql = """
        create table machine(
            id serial not null unique primary key,
            hostname varchar(253) not null unique
        );
        create table metrics(
            id bigserial not null unique primary key,
            machine_id integer references machine(id) not null,
            time timestamp not null,
            uptime integer not null,
            cpu_usage real not null,
            disk_usage real not null
        );
    """

    pg_cur = pg_con.cursor()
    try:
        pg_cur.execute(create_table_sql)
        print("Table created successfully")
    except psycopg2.errors.DuplicateTable:
        print("Table already exist")
    pg_cur.close()

