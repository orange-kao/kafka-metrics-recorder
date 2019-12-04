#!/usr/bin/python3

import socket
import time
import os
import json

from linux_metrics import cpu_stat
from linux_metrics import disk_stat

class LazyMetrics:
    def __init__(self, config):
        self.config = config["metrics"]

    @staticmethod
    def dict_to_bytes(metrics_dict):
        metrics_bytes = json.dumps(metrics_dict).encode()
        return metrics_bytes
        
    @staticmethod
    def bytes_to_dict(metrics_bytes):
        metrics_dict = json.loads(metrics_bytes.decode())
        return metrics_dict

    def get_bytes(self):
        metrics_dict = self.get_dict()
        metrics_bytes = self.dict_to_bytes(metrics_dict)
        return metrics_bytes

    def get_dict(self):
        hostname = socket.gethostname()

        # https://pypi.org/project/linux-metrics/
        # Reading CPU usage will block for report_frequency seconds
        report_frequency = float(self.config["report_frequency"])
        cpu_util = cpu_stat.cpu_percents(report_frequency)
        cpu_usage = 100 - cpu_util['idle']

        disk_util = disk_stat.disk_usage(self.config["mount_point"])
        disk_usage = disk_util[2] * 100.0 / disk_util[1]

        loadavg_tuple = os.getloadavg()


        # Keep getting uptime and system clock closer to the end of this
        # function. It will help to keep it close with Kafka timestamp.

        # Get system uptime
        # http://planzero.org/blog/2012/01/26/system_uptime_in_python,_a_better_way
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])

        # System time, epoch
        # Timezone independent (always based on UTC time in 1970)
        sys_time_epoch = time.time()

        return {"hostname":hostname,
                "cpu_usage":cpu_usage,
                "disk_usage":disk_usage,
                "loadavg_1":loadavg_tuple[0],
                "loadavg_5":loadavg_tuple[1],
                "loadavg_15":loadavg_tuple[2],
                "uptime_seconds":uptime_seconds,
                "sys_time_epoch":sys_time_epoch,
               }

