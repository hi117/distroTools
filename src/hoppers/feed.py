from time import time, sleep
import utils.configParser as configParser
from utils.importhelper import load

'''
queue is structred as so:
    [
    [runtime, feed]
    ]
'''
queue = []

config = {}

def calcNextRuntime(feed):
    '''
    This function takes a feed and evaluetes its scedule to determine at what 
    time it should be run next.
    '''
    # caculate seconds until next run
    units = {
            's': 1,
            'm': 60,
            'h': 3600,
            'd': 86400,
            'w': 604800,
            'mo': 2592000, # month assumes 30 days
            'y': 31536000 # year assumes 365 days
            }
    if feed.scedule[-1] in units:
        scedule = int(feed.scedule[:-1]) * units[feed.scedule[-1]]
    else:
        scedule = int(feed.scedule)
    
    return scedule + time()

def insertQueue(feed):
    '''
    Inserts a feed into the queue.
    '''
    runtime = calcNextRuntime(feed)
    a = len(queue) + 1
    for n, i in enumerate(queue):
        if runtime < i[0]:
            a = n
            break
    queue.insert(a, [runtime, feed])

def sleepUntilNext():
    sleep(time() - queue[0][0])

def parseConfig():
    config = configParser.parse('feed.conf')['']

def run(pipe):
    # parse the config
    parseConfig()
    
    # load all the feeds
    feeds = []
    for i in config['feeds']:
        feeds.append(load(config['feeddir'] + '/' + i + '.py'))

    # generate the inital queue
    for i in feeds:
        insertQueue(i)

    # main loop
    while True:
        sleepUntilNext()
        # check if we got interrupted for some reason
        if time() < queue[0][0]:
            continue
        feed = queue.pop(0)[1]
        # run the feed and send it to the updater
        for i in feed.run():
            pipe.send(i)


