import os
import json
import sys

def _load_conf():
    with open("test_env.toml", "rb") as conf:
        if sys.version_info[1] >= 11:
            import tomllib
            return tomllib.load(conf)
        else: 
            import toml 
            return toml.load(conf) 

def set_env():
    config_data = _load_conf()
    for key, value in config_data.items():
        if type(value) == list:
            os.environ[key] = json.dumps(value)
            continue
        for k, v in value.items():
            os.environ[k] = str(v)
