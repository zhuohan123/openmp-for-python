import omp
import time
import random

def barrier_test():
    # omp parallel
    print str(omp.get_thread_num()) + ' a\n',
    time.sleep(random.randrange(3))
    print str(omp.get_thread_num()) + ' b\n',
    time.sleep(random.randrange(3))
    # omp barrier
    print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end

barrier_test()