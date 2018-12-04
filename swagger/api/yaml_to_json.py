import time
import yaml
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class ChangeYamlHandler(FileSystemEventHandler):
    def __init__(self, fname):
        self.fname = fname

    def on_modified(self, event):
        if isinstance(event, FileModifiedEvent) and (event.src_path == self.fname):
            print("Modification detected, converting yaml to json...")
            with open("swagger.yaml") as yaml_file, open("swagger.json", "w") as json_file:
                obj = yaml.load(yaml_file)
                json_file.write(json.dumps(obj, indent=4))
                print(self.fname, " has been converted to *.json")


if __name__ == "__main__":
    path = "."
    event_handler = ChangeYamlHandler("./swagger.yaml")
    observer = Observer()
    observer.schedule(event_handler, path)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
