import omp
import time
import random


def hello_world():
    print "i write dazuoye!!!"
    print omp.get_thread_num(), '/', omp.get_num_threads()
    a = 2017
    # omp parallel num_threads(4)
    print "i love bianyishixi!\n",
    print '%d / %d\n' % (omp.get_thread_num(), omp.get_num_threads()),
    print "a = " + str(a) +'\n',
    # omp parallel end


hello_world()

num_step = 100000
step = 1.0 / num_step

def calc_pi():
    ans = [0] * 8
    # omp parallel num_threads(8) private(i,tid,nthrds,tmp_ans,x)
    tid = omp.get_thread_num()
    nthrds = omp.get_num_threads()
    print "working: " + str(tid) + ' / ' + str(nthrds) + '\n',
    tmp_ans = 0
    for i in xrange(tid, num_step, nthrds):
        x = (i + 0.5) * step
        tmp_ans += 4.0 / (1.0 + x * x)
    ans[tid] = tmp_ans
    # omp parallel end
    print sum(ans) * step


calc_pi()


def calc_pi_for():
    ans = 0
    lock = omp.init_lock()
    # omp parallel num_threads(8) private(i,x)
    # omp for reduction(+:ans)
    for i in range(num_step):
        x = (i + 0.5) * step
        ans += 4.0 / (1.0 + x * x)
    # omp parallel end
    print ans * step


calc_pi_for()


def calc_pi_critical():
    ans = 0
    lock = omp.init_lock()
    # omp parallel num_threads(8) private(i,x)
    # omp for
    for i in range(num_step):
        x = (i + 0.5) * step
        # omp critical
        ans += 4.0 / (1.0 + x * x)
        # omp critical end
    # omp parallel end
    print ans * step


calc_pi_critical()


def sections_test():
    # omp parallel num_threads(2)
    # omp sections
    # omp section
    print 'section 0 from ' + str(omp.get_thread_num()) + '\n',
    # omp section end
    # omp section
    print 'section 1 from ' + str(omp.get_thread_num()) + '\n',
    # omp section end
    # omp sections end
    # omp parallel end


sections_test()


def barrier_test():
    # omp parallel
    print str(omp.get_thread_num()) + ' a\n',
    time.sleep(random.randrange(3))
    # omp barrier
    print str(omp.get_thread_num()) + ' b\n',
    time.sleep(random.randrange(3))
    # omp barrier
    print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end
