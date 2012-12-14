import os

def run(pipe):
    # create a fifo
    os.mkfifo('manual.fifo')
    with open('manual.fifo','r') as f:
        while not f.closed:
            a=f.readline()
            pipe.send(a.split(','))
