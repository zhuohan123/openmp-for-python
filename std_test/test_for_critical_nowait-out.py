import omp
omp.set_num_of_internal_locks(2)
num_step = 1000000
step = 1.0 / num_step
def calc_pi_critical():
    _dict1={}
    _dict1['ans'] = 0
    # omp parallel num_threads(8) private(i,x)
    def _block0():
        # omp for nowait
        for i in omp.prange(num_step):
            x = (i + 0.5) * step
            # omp critical
            omp.set_internal_lock(1)
            _dict1['ans'] += 4.0 / (1.0 + x * x)
            omp.unset_internal_lock(1)
            # omp critical end
    # omp parallel end
    omp.parallel_run(_block0,8)
    print _dict1['ans'] * step
calc_pi_critical()
pass

