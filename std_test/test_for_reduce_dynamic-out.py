import omp
omp.set_num_of_internal_locks(1)
num_step = 1000000
step = 1.0 / num_step
def calc_pi_for():
    _dict1={}
    _dict1['ans'] = 0
    # omp parallel num_threads(8) private(i,x)
    def _block0():
        # omp for reduction(+:ans) schedule(dynamic)
        OMP_REDUCTION_VAR_0_0 = omp.reduction_init('+')
        for i in omp.drange(num_step):
            x = (i + 0.5) * step
            OMP_REDUCTION_VAR_0_0 += 4.0 / (1.0 + x * x)
        omp.set_internal_lock(0)
        _dict1['ans'] = omp.reduction('+',_dict1['ans'],OMP_REDUCTION_VAR_0_0)
        omp.unset_internal_lock(0)
        omp.barrier()
    # omp parallel end
    omp.parallel_run(_block0,8)
    print _dict1['ans'] * step
calc_pi_for()
pass

