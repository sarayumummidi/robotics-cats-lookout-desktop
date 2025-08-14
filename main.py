from src import *
import time
import threading

settings = load_settings("settings.json")

if __name__ == "__main__":
    instances = create_instances(settings)
    threads = []

    for instance in instances:
        t = threading.Thread(target=instance.start)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping all instances...")
        for instance in instances:
            instance.stop()
        for t in threads:
            t.join()