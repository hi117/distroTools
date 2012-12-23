import os
from os.path import exists
import utils.configParser as configParser
from time import sleep

def run(pipe):
    # parse the config
    config = configParser.parse('manual.conf')['']
    
    # create a fifo
    if not exists(config['fifoPath']):
        os.mkfifo(config['fifoPath'])
    with open(config['fifoPath'], 'r') as f:
        while not f.closed:
            a = f.readline()
            if a != '':
                pipe.send(a.split(','))
            sleep(2)
