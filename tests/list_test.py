def prange(start, stop=None, step=1, id=0, nthrds=1):
    if stop is None:
        stop = start
        start = 0
    if step == 0:
        raise ValueError('step can not be zero.');
    return xrange(start+id*step, stop, nthrds*step)

def plist(iter_list, id=0, nthrds=1):
    l = list(iter_list)
    return l[id::nthrds]

nthrds = 5


for i in range(nthrds):
    print list(plist(range(20),id=i, nthrds=nthrds))


