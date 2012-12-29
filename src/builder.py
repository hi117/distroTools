from multiprocessing import Pipe, Process
from utils.importhelper import load

config = {}

class package:
    def __init__(self, name, config):
        self.name = name
        self.config = config
        self.hasBuilt = False
        self.hasError = None

def processConfig(config):
    config['storages'] = map(lambda a: a.strip(), config['storages'].split(','))
    return config


