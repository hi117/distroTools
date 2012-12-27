'''
This file contains functions that help with the dependancy determination
of C files.  It scans headers and function declarations to determine which
dependancies are needed by each package.

Due to the amazingness of gcc, what would have been an extremely hard problem
was compressed down to a single subprocess.call due to the -E flag.
'''

import re
from subprocess import check_output

def owns(path):
    '''
    This function takes a path and runs pacman -Qo on it and parses out the
    package name returned or None if the path is unowned.
    '''
    try:
        ret = check_output(['pacman','-Qo',path])
        return ret.split(b' ')[4]
    except:
        return None


def header2package(header):
    '''
    This function returns the package that owns the system header file.
    '''
    return owns('/usr/include/' + header)

def packagesNeeded(path):
    '''
    Scans a file for #includes and determines which package(s) 
    are needed to build the file.
    '''
    # determine system includes
    includes = []
    with open(path,'r') as f:
        for line in f.readlines():
            match = re.match('\s*#include\s+<(\w+[.]h)>', line, flags = re.IGNORECASE)
            if match:
                includes.append(match.group(1))
    # generate the package owner
    owners = []
    for i in includes:
        owner = header2package(i)
        if not owner in owners:
            owners.append(owner)
    return owners
