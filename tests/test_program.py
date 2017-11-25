import omp

def count(n):
    s = 0
    #omp parallel private(i)
    #omp for reduction(+:s)
    for i in xrange(n):
        s += i
    #omp parallel end
    return s

print count(1000000000)
