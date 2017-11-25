import omp
omp.set_num_of_internal_locks(1)
import time
import random
def haswait_test():
    _dict1={}
    # omp parallel num_threads(8) private(i)
    def _block0():
        # omp for
        for i in omp.prange(8):
        	time.sleep(random.randrange(3))
            print str(omp.get_thread_num()) + ' thread\n',
        omp.barrier()
        print "done"
    # omp parallel end
    omp.parallel_run(_block0,8)
haswait_test()
pass

