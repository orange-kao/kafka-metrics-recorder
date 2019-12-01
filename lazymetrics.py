#!/usr/bin/python3

import socket
import time
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
        cpu_util = cpu_stat.cpu_percents(float(self.config["report_frequency"]))
        cpu_usage = 100 - cpu_util['idle']
        disk_util = disk_stat.disk_usage(self.config["mount_point"])
        disk_usage = disk_util[2] * 100.0 / disk_util[1]

        # http://planzero.org/blog/2012/01/26/system_uptime_in_python,_a_better_way
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])

        sys_time_epoch = time.time()

        print("Hostname: %s" % hostname)
        print("CPU usage: %f" % cpu_usage)
        print("Disk usage: %f %%" % disk_usage)
        print("Uptime: %f" % uptime_seconds)
        return {"hostname":hostname,
                "cpu_usage":cpu_usage,
                "disk_usage":disk_usage,
                "uptime_seconds":uptime_seconds,
                "sys_time_epoch":sys_time_epoch,
               }

