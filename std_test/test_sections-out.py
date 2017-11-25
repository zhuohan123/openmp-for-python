import omp
omp.set_num_of_internal_locks(0)
def sections_test():
    _dict1={}
    # omp parallel num_threads(2)
    def _block0():
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
    omp.parallel_run(_block0,2)
sections_test()
pass

