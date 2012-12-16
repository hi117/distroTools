def parse(path,subsections=[]):
    '''
    This function parses a configuration file consisting of k=v pairs.
    It also has support for subsection reading in the form of [subsection] form.
    '''
    lines = False
    with open(path,'r') as f:
        lines = f.readlines()
    if not lines:
        return {}
    out={
            '': {}
        }
    canRead = True
    curSub = ''
    for line in lines:
        line = line.strip()
        # Check if there is anything on the line
        if len(line) == 0:
            continue
        # Check for comments beginning with #
        if line[0] == '#':
            continue
        if (line[0] == '[') and (line[-1] == ']'):
            # its a subsection
            line = line[1:-1]
            if line in subsections: 
                canRead = True
                curSub = line
                out[line] = {}
            else: canRead = False
            continue
        if canRead:
            # Read the k,v pair if there is one
            line=line.split('=')
            if len(line) < 2:
                continue
            if len(line) > 2:
                line[1] = '='.join(line[1:])
            line[0] = line[0].strip()
            line[1] = line[1].strip()
            out[curSub][line[0]] = line[1]
    return out
