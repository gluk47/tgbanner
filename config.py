import os
import yaml
import re
import itertools
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import logging

logger = logging.getLogger("banhammer")

class ConfigReloadHandler(FileSystemEventHandler):
    def __init__(self, config_path, reload_callback):
        self.config_path = config_path
        self.reload_callback = reload_callback

    def on_modified(self, event):
        if event.src_path.rsplit('/', 1)[-1] == self.config_path:
            self.reload_callback()

def start_watcher(config_path):
    event_handler = ConfigReloadHandler(config_path, lambda: reload(config_path))
    observer = Observer()
    cfgdir = os.path.dirname(os.path.realpath(config_path))
    observer.schedule(event_handler, path=cfgdir, recursive=False)
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    return observer

def load(path):
    global BLACKLIST_RE
    logger.info('Loading config from %s', path)
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
        API_TOKEN = config.get('token')
        BLACKLIST = config['blacklist']

    BLACKLIST_RE = make_re(BLACKLIST)
    return API_TOKEN, BLACKLIST_RE

def reload(config_path):
    global BLACKLIST_RE
    try:
        _, BLACKLIST_RE = load(config_path)
    except Exception as x:
        logger.error(f'Failed to reload config, ignored: {x}')

def make_re(lst):
    wb = r'\b'
    return re.compile('|'.join(
        f'({wb}{w.replace(" ", " +")}{wb if w[-1] not in ("+$") else ""})'
        for w in itertools.chain(*lst.values())
    ))

BLACKLIST_RE = None