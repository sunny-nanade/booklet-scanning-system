import json
import os

CONFIG_PATH = "config.json"

DEFAULT_CONFIG = {
    "cameraId": None,
    "resolution": {"width": 640, "height": 480},
    "flipH": False,
    "flipV": False,
    "cropLeft": {"x": 0, "y": 0, "width": 320, "height": 480},
    "cropRight": {"x": 320, "y": 0, "width": 320, "height": 480},
    "supplementPageCount": 4
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=2)

def update_config_field(key, value):
    config = load_config()
    config[key] = value
    save_config(config)
    return config
