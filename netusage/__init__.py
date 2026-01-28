import time
from typing import Dict

import psutil

_monitoring_state = {}


def get_network_io() -> tuple[int, int]:
    """
    Get system-wide network I/O counters.

    Returns:
        tuple: (bytes_sent, bytes_received)
    """
    net_io = psutil.net_io_counters()
    return net_io.bytes_sent, net_io.bytes_recv


def get_network_connections_count(pid: int) -> int:
    """
    Get current network connections count for a process.

    Args:
        pid: Process ID to monitor

    Returns:
        int: Number of active network connections
    """
    try:
        proc = psutil.Process(pid)
        connections = proc.net_connections(kind="inet")
        return len(connections)
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        return 0


def start_monitoring(pid: int) -> None:
    """
    Start monitoring network activity for a process.

    Args:
        pid: Process ID to monitor
    """
    sent_before, recv_before = get_network_io()
    conn_count = get_network_connections_count(pid)

    _monitoring_state[pid] = {
        "start_time": time.time(),
        "bytes_sent_before": sent_before,
        "bytes_recv_before": recv_before,
        "connections_start": conn_count,
        "max_connections": conn_count,
    }


def end_monitoring(pid: int) -> Dict:
    """
    End monitoring and return results.

    Args:
        pid: Process ID that was being monitored

    Returns:
        dict: Dictionary containing monitoring results with keys:
            - bytes_sent: Total bytes sent during monitoring
            - bytes_recv: Total bytes received during monitoring
            - sent_kb: Bytes sent in KB (formatted)
            - recv_kb: Bytes received in KB (formatted)
            - total_kb: Total data transferred in KB
            - connections: Current number of connections
            - duration: Monitoring duration in seconds
    """
    if pid not in _monitoring_state:
        raise ValueError(f"Monitoring was not started for PID {pid}")

    state = _monitoring_state[pid]

    # Get final measurements
    sent_after, recv_after = get_network_io()
    conn_count = get_network_connections_count(pid)
    end_time = time.time()

    # Calculate differences
    bytes_sent = sent_after - state["bytes_sent_before"]
    bytes_recv = recv_after - state["bytes_recv_before"]
    duration = end_time - state["start_time"]

    del _monitoring_state[pid]

    return {
        "bytes_sent": bytes_sent,
        "bytes_recv": bytes_recv,
        "sent_kb": round(bytes_sent / 1024, 2),
        "recv_kb": round(bytes_recv / 1024, 2),
        "total_kb": round((bytes_sent + bytes_recv) / 1024, 2),
        "connections": conn_count,
        "duration": round(duration, 2),
    }


__all__ = ["start_monitoring", "end_monitoring", "get_network_connections_count"]
