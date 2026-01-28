# netusage

A simple process traffic analyzer for Python

```python
import os
from network_monitor import start_monitoring, end_monitoring

pid = os.getpid()

start_monitoring(pid)

# Do your network operations
import urllib.request
response = urllib.request.urlopen('https://api.example.com/data')
data = response.read()

results = end_monitoring(pid)
print(results)
```

```python
{
    'bytes_sent': 912,
    'bytes_recv': 3552,
    'sent_kb': 0.89,
    'recv_kb': 3.47,
    'total_kb': 4.36,
    'connections': 1,
    'duration': 1.23
}
```
