import threading

print_lock = threading.Lock()


def log(msg):
    with print_lock:
        print(msg, flush=True)