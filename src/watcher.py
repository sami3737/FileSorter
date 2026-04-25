from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from src.script import organize
from src.config import SOURCE

# Watcher to monitor the source directory for new files and trigger the organization process automatically. It uses watchdog to listen for file creation events and calls the organize function when a new file is detected. The watcher runs indefinitely until interrupted by the user.
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