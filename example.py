from network_monitor import start_monitoring, end_monitoring

from urllib.request import urlopen

import os

pid = os.getpid()

start_monitoring(pid)

urlopen('https://google.com').read()

urlopen('https://youtube.com').read()

results = end_monitoring(pid)

print(results)
