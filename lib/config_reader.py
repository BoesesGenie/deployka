import json

def read_config():
    with open('config.json') as data_file:
        config = json.load(data_file)

        return config
