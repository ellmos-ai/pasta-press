import os
import json
import logging

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

# Default Konfiguration
DEFAULT_CONFIG = {
    "ollama_host": "http://localhost:11434",
    "model": "llama3.1",
    "output_suffix": "_pasta-press",
    "default_output_dir": None,
    "overwrite": False,
    "queue_file": "queue.json",
    "log_level": "INFO"
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            try:
                user_config = json.load(f)
                # Merge mit Default Config
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
            except json.JSONDecodeError:
                logging.error(f"Error parsing {CONFIG_FILE}. Using default values.")
                return DEFAULT_CONFIG.copy()
    else:
        # Erstelle initiales config file
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4)

# Lade Konfiguration beim Modulstart
CONFIG = load_config()

def setup_logger():
    log_level = getattr(logging, CONFIG.get("log_level", "INFO").upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger("PastaPress")

logger = setup_logger()
