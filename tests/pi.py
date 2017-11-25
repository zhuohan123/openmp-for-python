import omp

num_step = 300000000
step = 1.0 / num_step

def calc_pi_for():
    ans = 0
    # omp parallel num_threads(4) private(i,x)
    # omp for reduction(+:ans)
    for i in xrange(num_step):
        x = (i + 0.5) * step
        ans += 4.0 / (1.0 + x * x)
    # omp parallel end
    print "%.10f\n" % (ans * step),

calc_pi_for()


