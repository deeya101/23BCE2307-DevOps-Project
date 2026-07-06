import psutil
import socket
import time

GRAPHITE_HOST = 'localhost'
GRAPHITE_PORT = 2003
HOSTNAME = 'symposium-server'

def send_metric(sock, path, value, timestamp):
    message = f"{path} {value} {timestamp}\n"
    sock.sendall(message.encode('utf-8'))

def collect_and_send():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((GRAPHITE_HOST, GRAPHITE_PORT))
    print("Connected to Graphite. Sending metrics every 10 seconds... (Ctrl+C to stop)")

    try:
        while True:
            timestamp = int(time.time())

            cpu_percent = psutil.cpu_percent(interval=1)
            send_metric(sock, f"{HOSTNAME}.cpu.percent", cpu_percent, timestamp)

            memory = psutil.virtual_memory()
            send_metric(sock, f"{HOSTNAME}.memory.percent", memory.percent, timestamp)
            send_metric(sock, f"{HOSTNAME}.memory.used_mb", memory.used / (1024*1024), timestamp)

            disk = psutil.disk_usage('/')
            send_metric(sock, f"{HOSTNAME}.disk.percent", disk.percent, timestamp)
            send_metric(sock, f"{HOSTNAME}.disk.used_gb", disk.used / (1024**3), timestamp)

            net = psutil.net_io_counters()
            send_metric(sock, f"{HOSTNAME}.network.bytes_sent", net.bytes_sent, timestamp)
            send_metric(sock, f"{HOSTNAME}.network.bytes_recv", net.bytes_recv, timestamp)

            uptime_seconds = time.time() - psutil.boot_time()
            send_metric(sock, f"{HOSTNAME}.uptime.seconds", uptime_seconds, timestamp)

            print(f"[{timestamp}] Sent metrics: CPU={cpu_percent}% MEM={memory.percent}% DISK={disk.percent}%")
            time.sleep(9)
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        sock.close()

if __name__ == "__main__":
    collect_and_send()
