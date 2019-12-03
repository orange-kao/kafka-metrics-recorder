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

