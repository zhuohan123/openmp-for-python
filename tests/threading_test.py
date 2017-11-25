import threading
import time
import random
import omp
local_num = 0
def thread_cal():
    global local_num
    time.sleep(1)
    for _ in range(5):
        local_num += 1
        time.sleep(random.random())
        print threading.current_thread().getName(), local_num
    print omp.get_thread_num(),'/',omp.get_num_threads()

tmp_num_threads = omp.get_num_threads()
omp.set_num_threads(10)
threads = []
for i in range(omp.get_num_threads()):
    threads.append(threading.Thread(target=thread_cal,name=str(i)))
for t in threads:
    t.start()
for t in threads:
    t.join()
omp.set_num_threads(tmp_num_threads)

print threading.current_thread().getName()