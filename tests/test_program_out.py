import omp
omp.set_num_of_internal_locks(2)

def hello_world():
    print "i write dazuoye!!!"
    print omp.get_thread_num(),'/',omp.get_num_threads()
    a = 2017
    #omp parallel num_threads(4)
    print "i love bianyishixi!"
    print omp.get_thread_num(),'/',omp.get_num_threads()
    print "a =", a
    #omp parallel end

hello_world()

num_step = 10000
step = 1.0/num_step

def calc_pi():
    ans = [0] * 8
    #omp parallel num_threads(8) private(i,tid,nthrds,tmp_ans,x)
    tid = omp.get_thread_num()
    nthrds = omp.get_num_threads()
    print "working: "+str(tid)+' / '+str(nthrds)
    tmp_ans = 0
    for i in xrange(tid,num_step,nthrds):
        x = (i+0.5)*step
        tmp_ans += 4.0/(1.0 + x*x)
    ans[tid] = tmp_ans
    #omp parallel end
    print sum(ans)*step

calc_pi()

def calc_pi_for():
    ans = 0
    lock = omp.init_lock()
    tmp_ans = omp.reduction_init('+')
    #omp parallel num_threads(8) private(i,x)
    for i in omp.prange(num_step):
        x = (i+0.5)*step
        ans += 4.0/(1.0 + x*x)
    omp.set_internal_lock(0)
    tmp_ans = omp.reduction('+', tmp_ans, ans)
    omp.unset_internal_lock(0)
    omp.barrier()
    ans = tmp_ans
    #omp parallel end
    print ans * step

calc_pi_for()

def calc_pi_critical():
    ans = 0
    lock = omp.init_lock()
    #omp parallel num_threads(8) private(i,x)
    for i in omp.prange(num_step):
        x = (i+0.5)*step
        omp.set_internal_lock(1)
        ans += 4.0/(1.0 + x*x)
        omp.unset_internal_lock(1)
    #omp parallel end
    print ans * step

calc_pi_critical()

