import omp

def count(n):
    s = 0
    #omp parallel private(i) num_threads(4)
    if omp.get_thread_num()==0:
        print 'num_threads =', omp.get_num_threads()
    #omp for reduction(+:s)
    for i in xrange(n):
        s += i
    #omp parallel end
    return s
print count(500000000)
