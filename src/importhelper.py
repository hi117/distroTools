import imp
import os

def load(importf,fromd=os.getcwd()):
    return imp.load_source('.'.join(importf.split('.')[:-1]),fromd+'/'+importf)
