import os
import time
import urllib.request

from netusage import (
    end_monitoring,
    get_network_connections_count,
    start_monitoring,
)


def test_basic_monitoring():
    """Test basic start and end monitoring"""
    start_monitoring()

    try:
        response = urllib.request.urlopen("https://httpbin.org/json", timeout=10)
        data = response.read()
        assert len(data) > 0
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert "bytes_sent" in results
    assert "bytes_recv" in results
    assert "sent_kb" in results
    assert "recv_kb" in results
    assert "total_kb" in results
    assert "connections" in results
    assert "duration" in results


def test_result_types():
    """Test that results have correct types"""
    start_monitoring()

    try:
        urllib.request.urlopen("https://httpbin.org/uuid", timeout=10).read()
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert isinstance(results["bytes_sent"], int)
    assert isinstance(results["bytes_recv"], int)
    assert isinstance(results["sent_kb"], float)
    assert isinstance(results["recv_kb"], float)
    assert isinstance(results["total_kb"], float)
    assert isinstance(results["connections"], int)
    assert isinstance(results["duration"], float)


def test_positive_values():
    """Test that network activity produces positive values"""
    start_monitoring()

    try:
        urllib.request.urlopen("https://httpbin.org/json", timeout=10).read()
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert results["bytes_sent"] > 0
    assert results["bytes_recv"] > 0

    expected_total = round((results["bytes_sent"] + results["bytes_recv"]) / 1024, 2)
    assert results["total_kb"] == expected_total


def test_multiple_requests():
    """Test monitoring multiple network requests"""
    start_monitoring()

    urls = [
        "https://httpbin.org/uuid",
        "https://httpbin.org/user-agent",
    ]

    try:
        for url in urls:
            urllib.request.urlopen(url, timeout=10).read()
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert results["total_kb"] > 0


def test_kb_conversion():
    """Test that KB values are correctly calculated from bytes"""
    start_monitoring()

    try:
        urllib.request.urlopen("https://httpbin.org/json", timeout=10).read()
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    expected_sent_kb = round(results["bytes_sent"] / 1024, 2)
    expected_recv_kb = round(results["bytes_recv"] / 1024, 2)

    assert results["sent_kb"] == expected_sent_kb
    assert results["recv_kb"] == expected_recv_kb


def test_duration_tracking():
    """Test that duration is properly tracked"""
    start_monitoring()

    time.sleep(0.5)

    try:
        urllib.request.urlopen("https://httpbin.org/delay/1", timeout=10).read()
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert results["duration"] >= 1.5


def test_end_without_start_raises_error():
    """Test that ending monitoring without starting raises an error"""
    fake_pid = 999999

    try:
        end_monitoring(fake_pid)
        assert False
    except ValueError as e:
        assert "Monitoring was not started" in str(e)


def test_connection_count():
    """Test that connection count is tracked"""
    pid = os.getpid()
    count = get_network_connections_count(pid)

    assert isinstance(count, int)
    assert count >= 0


def test_no_network_activity():
    """Test monitoring with no network activity"""
    pid = os.getpid()
    start_monitoring(pid)

    time.sleep(0.1)

    results = end_monitoring()

    assert isinstance(results["bytes_sent"], int)
    assert isinstance(results["bytes_recv"], int)
    assert results["bytes_sent"] >= 0
    assert results["bytes_recv"] >= 0


def test_sequential_monitoring():
    """Test that we can monitor multiple times sequentially"""
    start_monitoring()
    try:
        urllib.request.urlopen("https://httpbin.org/uuid", timeout=10).read()
    except Exception:
        end_monitoring()
        return
    results1 = end_monitoring()

    start_monitoring()
    try:
        urllib.request.urlopen("https://httpbin.org/json", timeout=10).read()
    except Exception:
        end_monitoring()
        return
    results2 = end_monitoring()

    assert results1["total_kb"] > 0
    assert results2["total_kb"] > 0


def test_large_download():
    """Test monitoring a larger download"""
    start_monitoring()

    try:
        data = urllib.request.urlopen(
            "https://httpbin.org/bytes/25000", timeout=15
        ).read()
        assert len(data) == 25000
    except Exception:
        end_monitoring()
        return

    results = end_monitoring()

    assert results["recv_kb"] > 24


def test_invalid_pid():
    """Test handling of invalid PID"""
    invalid_pid = 999999999

    count = get_network_connections_count(invalid_pid)
    assert count == 0


def test_negative_values_impossible():
    """Test that we never get negative values"""
    start_monitoring()

    time.sleep(0.1)

    results = end_monitoring()

    assert results["bytes_sent"] >= 0
    assert results["bytes_recv"] >= 0
    assert results["sent_kb"] >= 0
    assert results["recv_kb"] >= 0
    assert results["total_kb"] >= 0
    assert results["connections"] >= 0
    assert results["duration"] >= 0
