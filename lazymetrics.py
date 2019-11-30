#!/usr/bin/python3

import socket
import time

from linux_metrics import cpu_stat
from linux_metrics import disk_stat

def collect(config):
    hostname = socket.gethostname()

    # https://pypi.org/project/linux-metrics/
    cpu_util = cpu_stat.cpu_percents(1)
    cpu_usage = 100 - cpu_util['idle']
    disk_util = disk_stat.disk_usage(config["metric"]["mount_point"])
    disk_usage = disk_util[2] * 100.0 / disk_util[1]

    # http://planzero.org/blog/2012/01/26/system_uptime_in_python,_a_better_way
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    time_epoch = time.time()

    print("Hostname: %s" % hostname)
    print("CPU usage: %f" % cpu_usage)
    print("Disk usage: %f %%" % disk_usage)
    print("Uptime: %f" % uptime_seconds)
    return {"hostname":hostname,
            "cpu_usage":cpu_usage,
            "disk_usage":disk_usage,
            "uptime_seconds":uptime_seconds,
            "time_epoch":time_epoch,
           }

