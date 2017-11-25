import omp
import time
import random

def nowait_test():
    # omp parallel num_threads(8) private(i)
    # omp for nowait
    for i in range(8):
    	time.sleep(random.randrange(3))
        print str(omp.get_thread_num()) + ' thread\n',
    print "done"
    # omp parallel end

nowait_test()