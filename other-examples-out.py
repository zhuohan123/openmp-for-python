import omp
omp.set_num_of_internal_locks(3)
import time
import random
def hello_world():
    _dict1={}
    print "i write dazuoye!!!"
    print omp.get_thread_num(), '/', omp.get_num_threads()
    _dict1['a'] = 2017
    # omp parallel num_threads(4)
    def _block0():
        print "i love bianyishixi!\n",
        print '%d / %d\n' % (omp.get_thread_num(), omp.get_num_threads()),
        print "a = " + str(_dict1['a']) +'\n',
    # omp parallel end
    omp.parallel_run(_block0,4)
hello_world()
num_step = 100000
step = 1.0 / num_step
def calc_pi():
    _dict2={}
    _dict2['ans'] = [0] * 8
    # omp parallel num_threads(8) private(i,tid,nthrds,tmp_ans,x)
    def _block1():
        tid = omp.get_thread_num()
        nthrds = omp.get_num_threads()
        print "working: " + str(tid) + ' / ' + str(nthrds) + '\n',
        tmp_ans = 0
        for i in xrange(tid, num_step, nthrds):
            x = (i + 0.5) * step
            tmp_ans += 4.0 / (1.0 + x * x)
        _dict2['ans'][tid] = tmp_ans
    # omp parallel end
    omp.parallel_run(_block1,8)
    print sum(_dict2['ans']) * step
calc_pi()
def calc_pi_for():
    _dict3={}
    _dict3['ans'] = 0
    _dict3['lock'] = omp.init_lock()
    # omp parallel num_threads(8) private(i,x)
    def _block2():
        # omp for reduction(+:ans)
        OMP_REDUCTION_VAR_0_0 = omp.reduction_init('+')
        for i in omp.prange(num_step):
            x = (i + 0.5) * step
            OMP_REDUCTION_VAR_0_0 += 4.0 / (1.0 + x * x)
        omp.set_internal_lock(0)
        _dict3['ans'] = omp.reduction('+',_dict3['ans'],OMP_REDUCTION_VAR_0_0)
        omp.unset_internal_lock(0)
        omp.barrier()
    # omp parallel end
    omp.parallel_run(_block2,8)
    print _dict3['ans'] * step
calc_pi_for()
def calc_pi_critical():
    _dict4={}
    _dict4['ans'] = 0
    _dict4['lock'] = omp.init_lock()
    # omp parallel num_threads(8) private(i,x)
    def _block3():
        # omp for
        for i in omp.prange(num_step):
            x = (i + 0.5) * step
            # omp critical
            omp.set_internal_lock(2)
            _dict4['ans'] += 4.0 / (1.0 + x * x)
            omp.unset_internal_lock(2)
        omp.barrier()
            # omp critical end
    # omp parallel end
    omp.parallel_run(_block3,8)
    print _dict4['ans'] * step
calc_pi_critical()
def sections_test():
    _dict5={}
    # omp parallel num_threads(2)
    def _block4():
        # omp sections
        for OMP_SECTIONS_ID in omp.prange(2):
        # omp section
            if OMP_SECTIONS_ID == 0:
                print 'section 0 from ' + str(omp.get_thread_num()) + '\n',
        # omp section end
        # omp section
            if OMP_SECTIONS_ID == 1:
                print 'section 1 from ' + str(omp.get_thread_num()) + '\n',
        # omp section end
        # omp sections end
        omp.barrier()
    # omp parallel end
    omp.parallel_run(_block4,2)
sections_test()
def barrier_test():
    _dict6={}
    # omp parallel
    def _block5():
        print str(omp.get_thread_num()) + ' a\n',
        time.sleep(random.randrange(3))
        # omp barrier
        omp.barrier()
        print str(omp.get_thread_num()) + ' b\n',
        time.sleep(random.randrange(3))
        # omp barrier
        omp.barrier()
        print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end
    omp.parallel_run(_block5,0)
barrier_test()
pass

