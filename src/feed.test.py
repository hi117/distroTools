'''
This program is intended to assist in testing the feed hopper module.
'''
from multiprocessing import Pipe, Process
import hoppers.feed as feed
recvp, sendp = Pipe()
p = Process(target = feed.run, args = (sendp,))
print('Starting feed')
p.start()
while p.is_alive():
    if recvp.poll(1):
        print(recvp.recv())
p.join()

