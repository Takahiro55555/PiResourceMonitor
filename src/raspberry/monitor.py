import datetime
import time
import subprocess
import sys
import signal

import requests

from settings import *

class Monitor:
    def __init__(self):
        self._tck_list = self.get_cpu_stat()
        self._time_stamp = -1
        self._cpu_freq = -1
        self._cpu_temp = -1
        self._cpu_usage_total = -1
        self._cpu_usage_each = []
        self._memory_usage = -1
        self._swap_usage = -1
    
    def send(self, arg1, arg2):
        self.get_all_stat()
        data = {
            "host_name": HOST_NAME,
            "max_row": MAX_LINE,
            "time_stamp": self._time_stamp,
            "cpu_freq": self._cpu_freq,
            "cpu_temp": self._cpu_temp,
            "cpu_usage_total": self._cpu_usage_total,
            "mem_usage": self._memory_usage,
            "swap_usage": self._swap_usage
        }
        for i in range(len(self._cpu_usage_each)):
            key = "cpu_usage_%02d" % (i + 1)
            data[key] = self._cpu_usage_each[i]
        self.post_data(data)

    def get_all_stat(self):
        now = datetime.datetime.now()
        cmd = "vcgencmd measure_clock arm && vcgencmd measure_temp && free"
        rstd_outs ,_ = Monitor.exec_command(cmd)
        line_list = rstd_outs.split("\n")
        rstd_out_cpu_freq = line_list[0]
        rstd_out_cpu_temp = line_list[1]
        rstd_out_memory = line_list[-3]
        rstd_out_swap = line_list[-2]
        self._cpu_freq = int(rstd_out_cpu_freq.split("=")[1])
        self._cpu_temp = float(rstd_out_cpu_temp.split("=")[1].replace("'C", ""))
        memory_status = rstd_out_memory.split()
        memory_total = int(memory_status[1])
        memory_available = int(memory_status[3])
        self._memory_usage = round((1 - memory_available / memory_total) * 100)
        swap_status = rstd_out_swap.split()
        self._swap_usage = int(swap_status[2])
        self.get_cpu_usage()
        self._time_stamp = now.strftime("%Y/%m/%d %H:%M:%S.%f")

    def get_cpu_usage(self):
        tck_list_pre = self._tck_list
        tck_list_now = self.get_cpu_stat()
        self._tck_list = tck_list_now
        cpu_usage_list = []
        for (tck_now, tck_pre) in zip(tck_list_now, tck_list_pre):
            tck_dif = [now - pre for (now, pre) in zip(tck_now, tck_pre)]
            tck_busy = tck_dif[0]
            tck_all  = tck_dif[1]
            cpu_usage = int(tck_busy * 100 / tck_all)
            cpu_usage_list.append(cpu_usage)
        self._cpu_usage_total = cpu_usage_list[0]
        self._cpu_usage_each = cpu_usage_list[1:]
        
    @staticmethod
    def get_cpu_stat():
        cmd = 'cat /proc/stat | grep cpu'
        rstd_out ,_ = Monitor.exec_command(cmd)
        line_list = rstd_out.splitlines()
        tck_list = []
        for line in line_list:
            item_list = line.split()
            tck_idle = int(item_list[4])
            tck_busy = int(item_list[1])+int(item_list[2])+int(item_list[3])
            tck_all  = tck_busy + tck_idle
            tck_list.append( [ tck_busy ,tck_all ] )
        return tck_list
    
    @staticmethod
    def exec_command(cmd):
        result = subprocess.Popen(cmd, shell=True,  stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        rstdout, rstderr = result.communicate()
        return rstdout, rstderr

    @staticmethod
    def post_data(data):
        try:
            requests.post(GAS_URL, data=data)
        except KeyboardInterrupt:
            sys.exit()
        except requests.exceptions.ConnectionError:
            # 時々このエラーが発生するため追加
            print("Error, 送信失敗, %s" % data["time_stamp"])

if __name__ == "__main__":
    monitor = Monitor()
    #signal.signal(signal.SIGALRM, monitor.send)
    #signal.setitimer(signal.ITIMER_REAL, 1, SAMPLING_INTERVAL_SEC)
    while True:
        monitor.send(1, 2)
        #time.sleep(1)