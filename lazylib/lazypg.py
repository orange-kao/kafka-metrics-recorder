#!/usr/bin/python3

import datetime

import psycopg2
from psycopg2.errors import UniqueViolation
from psycopg2.extras import DictCursor
from psycopg2.extras import RealDictCursor
from psycopg2.extras import NamedTupleCursor

class LazyPg:
    def __init__(self, config):
        self.config = config["kafka"]
        self.pg_config = self.generate_connection_config(config["pg"])
        self.con = psycopg2.connect(**self.pg_config)

    def close(self):
        if self.con != None:
            self.con.close()
        self.config = None
        self.pg_config = None
        self.con = None

    @staticmethod
    def generate_connection_config(config):
        # http://initd.org/psycopg/docs/module.html

        # Documentation for sslmode
        # https://www.postgresql.org/docs/current/libpq-connect.html

        pg_config = {}
        pg_config["host"] = config["host"]
        pg_config["port"] = config["port"]
        pg_config['sslmode'] = "verify-full"
        pg_config['sslrootcert'] = config["ca_file"]
        pg_config["user"] = config["user"]
        pg_config["password"] = config["password"]
        pg_config["dbname"] = config["database"]
        return pg_config

    def drop_table(self):
        drop_table_sql = """
            drop table if exists metrics;
            """
        pg_cur = self.con.cursor()
        pg_cur.execute(drop_table_sql)
        pg_cur.close()
        self.con.commit()

    def create_table(self):
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

        # Postgres date type 'real': IEEE 754 single precision
        # https://www.postgresql.org/docs/current/datatype-numeric.html

        # Use kafka partition and offset as primary key to avoid
        # duplication
        create_table_sql = """
            create table metrics(
                kafka_partition smallint not null,
                kafka_offset bigint not null,
                primary key (kafka_partition, kafka_offset),
                hostname varchar(253) not null,
                cpu_usage real not null,
                disk_usage real not null,
                loadavg_1 real not null,
                loadavg_5 real not null,
                loadavg_15 real not null,
                uptime double precision not null,
                sys_time timestamp not null,
                kafka_time timestamp not null
            );
        """

        pg_cur = self.con.cursor()
        try:
            pg_cur.execute(create_table_sql)
        except psycopg2.errors.DuplicateTable:
            pass  # Table already exist
        pg_cur.close()
        self.con.commit()

    def insert_metrics(self, kafka_rec, metrics_dict):

        # Recording sys_time and kafka_time may help detecting system
        # clock drift (when NTP is out of sync)
        sql_template = """
            insert into metrics(
                kafka_partition,
                kafka_offset,
                hostname,
                cpu_usage,
                disk_usage,
                loadavg_1,
                loadavg_5,
                loadavg_15,
                uptime,
                sys_time,
                kafka_time
            )
            values( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Every timestamp in the DB will be UTC
        # Specify timezone for fromtimestamp() is required, otherwise it
        # would be local time
        # https://docs.python.org/3/library/datetime.html
        row_tuple = (
            kafka_rec.partition,
            kafka_rec.offset,
            metrics_dict.get("hostname"),
            metrics_dict.get("cpu_usage"),
            metrics_dict.get("disk_usage"),
            metrics_dict.get("loadavg_1"),
            metrics_dict.get("loadavg_5"),
            metrics_dict.get("loadavg_15"),
            metrics_dict.get("uptime_seconds"),
            datetime.datetime.fromtimestamp(
                metrics_dict["sys_time_epoch"], datetime.timezone.utc),
            datetime.datetime.fromtimestamp(
                kafka_rec.timestamp/1000, datetime.timezone.utc ),
            )

        pg_cur = self.con.cursor()
        try:
#            print(pg_cur.mogrify(sql_template, row_tuple))
            pg_cur.execute(sql_template, row_tuple)
        except UniqueViolation:
            pass  # Entry is already in the DB, do nothing
        pg_cur.close()
        self.con.commit()

    def get_last_metrics(self):
        sql_template = """
            select * from metrics order by kafka_offset desc limit 1;
        """

        pg_cur = self.con.cursor(cursor_factory=DictCursor)
        pg_cur.execute(sql_template)
        result = pg_cur.fetchone()
        pg_cur.close()
        return result;

