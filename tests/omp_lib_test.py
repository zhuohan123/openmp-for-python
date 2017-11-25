import omp
import time
import random

def f():
    for i in omp.drange(10):
        print str(i)+' '+str(omp.get_thread_num())+'\n',
        time.sleep(omp.get_thread_num())

omp.parallel_run(f,4)

