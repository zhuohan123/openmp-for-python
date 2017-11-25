import omp

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