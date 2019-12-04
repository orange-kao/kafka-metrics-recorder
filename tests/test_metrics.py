#!/usr/bin/python3

import configparser
import unittest

from lazylib import lazymetrics

class TestLazyMetrics(unittest.TestCase):

    def test_metrics_type_in_dict(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        metrics_instance = lazymetrics.LazyMetrics(config)
        metrics_bytes = metrics_instance.get_bytes()
        metrics_dict = metrics_instance.bytes_to_dict(metrics_bytes)

        self.assertTrue(type(metrics_dict["hostname"]) is str)
        self.assertTrue(type(metrics_dict["cpu_usage"]) is float)
        self.assertTrue(type(metrics_dict["disk_usage"]) is float)
        self.assertTrue(type(metrics_dict["loadavg_1"]) is float)
        self.assertTrue(type(metrics_dict["loadavg_5"]) is float)
        self.assertTrue(type(metrics_dict["loadavg_15"]) is float)
        self.assertTrue(type(metrics_dict["uptime_seconds"]) is float)
        self.assertTrue(type(metrics_dict["sys_time_epoch"]) is float)

    def test_metrics_to_and_from_bytes(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')  # everything will be string

        metrics_instance = lazymetrics.LazyMetrics(config)
        metrics_dict = metrics_instance.get_dict()
        metrics_bytes = metrics_instance.dict_to_bytes(metrics_dict)
        metrics_dict2 = metrics_instance.bytes_to_dict(metrics_bytes)

        self.assertEqual(metrics_dict, metrics_dict2)

#        with self.assertRaises(TypeError):
#            s.split(2)

if __name__ == '__main__':
    unittest.main()

