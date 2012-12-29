from multiprocessing import Pipe, Process
from utils.importhelper import load

config = {}

def processConfig(config):
    config['storages'] = map(lambda a: a.strip(), config['storages'].split(','))
    return config


