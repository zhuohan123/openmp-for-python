import omp
omp.set_num_of_internal_locks(0)
import time
import random
def barrier_test():
    _dict1={}
    # omp parallel
    def _block0():
        print str(omp.get_thread_num()) + ' a\n',
        time.sleep(random.randrange(3))
        print str(omp.get_thread_num()) + ' b\n',
        time.sleep(random.randrange(3))
        # omp barrier
        omp.barrier()
        print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end
    omp.parallel_run(_block0,0)
barrier_test()
pass

