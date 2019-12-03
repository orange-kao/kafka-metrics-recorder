# kafka-metrics-recorder
It's a personal project to get familar with Python and Apache Kafka.

Producer
1. Collect Linux system metrics including CPU usage, disk utilisation, load average
2. Send the system metrics to Kafka topic

Consumer
1. Subscribe to Kafka topic and receive Linux system metrics
2. Insert system metrics into PostgreSQL database

Producer and consumer can run on different machines.

## Setting up
```
./1_os_packages_install

./2_python_packages_install

./3_configure
```

## Running tests
```
pytest-3
```

## Runing producer
```
./producer.py
```

## Runing consumer
```
./consumer.py
```

## TODO
- systemd/init.d script to run producer or consumer on boot
- Integration with Travis CI
- Test case reading from PostgreSQL

## Example
```
$ ./producer.py
Push to Kafka: b'{"hostname": "x8", "cpu_usage": 13.727959697732999, "disk_usage": 86.00097387024903, "loadavg_1": 1.31, "loadavg_5": 1.56, "loadavg_15": 1.32, "uptime_seconds": 207915.5, "sys_time_epoch": 1575375324.9601083}'
Push to Kafka: b'{"hostname": "x8", "cpu_usage": 9.171974522292999, "disk_usage": 86.00097387024903, "loadavg_1": 1.28, "loadavg_5": 1.55, "loadavg_15": 1.31, "uptime_seconds": 207916.71, "sys_time_epoch": 1575375326.1683404}'
Push to Kafka: b'{"hostname": "x8", "cpu_usage": 9.10240202275601, "disk_usage": 86.00097387024903, "loadavg_1": 1.28, "loadavg_5": 1.55, "loadavg_15": 1.31, "uptime_seconds": 207917.76, "sys_time_epoch": 1575375327.2109153}'
```

```
$ ./consumer.py
partition 0, offset 0: {'hostname': 'x8', 'cpu_usage': 13.727959697732999, 'disk_usage': 86.00097387024903, 'loadavg_1': 1.31, 'loadavg_5': 1.56, 'loadavg_15': 1.32, 'uptime_seconds': 207915.5, 'sys_time_epoch': 1575375324.9601083}
partition 0, offset 1: {'hostname': 'x8', 'cpu_usage': 9.171974522292999, 'disk_usage': 86.00097387024903, 'loadavg_1': 1.28, 'loadavg_5': 1.55, 'loadavg_15': 1.31, 'uptime_seconds': 207916.71, 'sys_time_epoch': 1575375326.1683404}
partition 0, offset 2: {'hostname': 'x8', 'cpu_usage': 9.10240202275601, 'disk_usage': 86.00097387024903, 'loadavg_1': 1.28, 'loadavg_5': 1.55, 'loadavg_15': 1.31, 'uptime_seconds': 207917.76, 'sys_time_epoch': 1575375327.2109153}
```

```
defaultdb=> select * from metrics;
 kafka_partition | kafka_offset | hostname | cpu_usage | disk_usage | loadavg_1 | loadavg_5 | loadavg_15 |  uptime   |          sys_time          |       kafka_time
-----------------+--------------+----------+-----------+------------+-----------+-----------+------------+-----------+----------------------------+-------------------------
               0 |            0 | x8       |    13.728 |     86.001 |      1.31 |      1.56 |       1.32 |  207915.5 | 2019-12-03 12:15:24.960108 | 2019-12-03 12:15:24.961
               0 |            1 | x8       |   9.17197 |     86.001 |      1.28 |      1.55 |       1.31 | 207916.71 | 2019-12-03 12:15:26.16834  | 2019-12-03 12:15:26.169
               0 |            2 | x8       |    9.1024 |     86.001 |      1.28 |      1.55 |       1.31 | 207917.76 | 2019-12-03 12:15:27.210915 | 2019-12-03 12:15:27.212
(3 rows)
```

