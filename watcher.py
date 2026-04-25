from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from tri import organize
from config import SOURCE

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            print("Nouveau fichier détecté")
            time.sleep(1)
            organize(mode="auto")

observer = Observer()
observer.schedule(Handler(), SOURCE, recursive=False)
observer.start()

print("Watcher actif...")

try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    observer.stop()

observer.join()