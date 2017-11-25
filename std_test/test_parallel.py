import omp

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