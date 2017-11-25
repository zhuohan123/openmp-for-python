import omp
omp.set_num_of_internal_locks(1)
import time
import random
num_step = 300000000
step = 1.0 / num_step
def calc_pi_for():
    _dict1={}
    _dict1['ans'] = 0
    # omp parallel num_threads(2) private(i,x)
    def _block0():
        # omp for reduction(+:ans)
        OMP_REDUCTION_VAR_0 = omp.reduction_init('+')
        for i in omp.prange(num_step):
            x = (i + 0.5) * step
            OMP_REDUCTION_VAR_0 += 4.0 / (1.0 + x * x)
        omp.set_internal_lock(0)
        _dict1['ans'] = omp.reduction('+',_dict1['ans'],OMP_REDUCTION_VAR_0)
        omp.unset_internal_lock(0)
        omp.barrier()
    # omp parallel end
    omp.parallel_run(_block0,2)
    print "%.9f\n" % (_dict1['ans'] * step),
calc_pi_for()
pass

