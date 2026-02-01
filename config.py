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
    def __init__(self, config_path):
        self.config_path = config_path

    def on_modified(self, event):
        global BLACKLIST_RE
        if event.src_path.rsplit('/', 1)[-1] == self.config_path:
            try:
                _, BLACKLIST_RE = load(self.config_path)
            except Exception as x:
                logger.error(f'Failed to reload config, ignored: {x}')


def start_watcher(config_path):
    event_handler = ConfigReloadHandler(config_path)
    observer = Observer()
    cfgdir = os.path.dirname(os.path.realpath(config_path))
    observer.schedule(event_handler, path=cfgdir, recursive=False)
    observer_thread = threading.Thread(target=observer.start, daemon=True)
    observer_thread.start()
    return observer


def load(path):
    global BLACKLIST_RE, CHAT_CONFIGS
    logger.info('Loading config from %s', path)
    with open(path, 'r') as f:
        config = yaml.safe_load(f)
        API_TOKEN = config.get('token')
        BLACKLIST = config['blacklist']
        CHAT_CONFIGS = load_chat_configs(config.get('chats', {}))

    BLACKLIST_RE = make_re(BLACKLIST)
    return API_TOKEN, BLACKLIST_RE


def make_re(lst):
    wb = r'\b'
    return re.compile('|'.join(
        f'({wb}{w.replace(" ", " +")}{wb if w[-1] not in ("+$") else ""})'
        for w in itertools.chain(*lst.values())
    ))


def load_chat_configs(chats_config):
    """Load chat configurations with default config and per-chat overrides."""
    default_config = chats_config.get('default', {})
    chat_configs = {}
    
    chat_configs['default'] = default_config
    
    for chat_id, chat_config in chats_config.items():
        if chat_id == 'default':
            continue
            
        merged_config = default_config.copy()
        merged_config.update(chat_config)
        chat_configs[chat_id] = merged_config
    
    logger.info(f'Loaded chat configs for {len(chat_configs)} chats')
    return chat_configs


def get_chat_config(chat_id, configs_by_chat={}):
    """Get configuration for a specific chat, falling back to default."""
    if chat_id in configs_by_chat:
        return configs_by_chat[chat_id]
    config = CHAT_CONFIGS.get('default', {
        'clean_system_messages': False,
        'blacklist': None
    }).copy()
    
    return config.update(CHAT_CONFIGS.get(str(chat_id), {}))


BLACKLIST_RE = None
CHAT_CONFIGS = {}
