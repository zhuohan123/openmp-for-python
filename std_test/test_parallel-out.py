import omp
omp.set_num_of_internal_locks(0)
def hello_world():
    _dict1={}
    print "i write dazuoye!!!"
    print omp.get_thread_num(),'/',omp.get_num_threads()
    _dict1['a'] = 2017
    #omp parallel num_threads(4)
    def _block0():
        print "i love bianyishixi!"
        print omp.get_thread_num(),'/',omp.get_num_threads()
        print "a =", _dict1['a']
    #omp parallel end
    omp.parallel_run(_block0,4)
hello_world()
pass

