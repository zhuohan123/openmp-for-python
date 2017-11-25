import omp
omp.set_num_of_internal_locks(1)
def count(n):
    _dict1={}
    _dict1['n']=n
    _dict1['s'] = 0
    #omp parallel private(i) num_threads(2)
    def _block0():
        if omp.get_thread_num()==0:
            print 'num_threads =', omp.get_num_threads()
        #omp for reduction(+:s)
        OMP_REDUCTION_VAR_0_0 = omp.reduction_init('+')
        for i in omp.prange(_dict1['n']):
            OMP_REDUCTION_VAR_0_0 += i
        omp.set_internal_lock(0)
        _dict1['s'] = omp.reduction('+',_dict1['s'],OMP_REDUCTION_VAR_0_0)
        omp.unset_internal_lock(0)
        omp.barrier()
    #omp parallel end
    omp.parallel_run(_block0,2)
    return _dict1['s']
print count(500000000)
pass

