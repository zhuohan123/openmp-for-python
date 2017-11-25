import threading

with open('cpu_count.txt', 'r') as _f:
    _cpu_count = int(_f.read())

def cpu_count():
    return _cpu_count

_num_threads = 1


def get_thread_num():
    thread_name = threading.current_thread().getName()
    if thread_name == 'MainThread':
        return 0
    else:
        return int(threading.current_thread().getName())


def get_num_threads():
    global _num_threads
    return _num_threads


def set_num_threads(n):
    global _num_threads
    _num_threads = n


# helper functions for for statement
def prange(start, stop=None, step=1):
    if stop is None:
        stop = start
        start = 0
    id = get_thread_num()
    nthrds = get_num_threads()
    if step == 0:
        raise ValueError('step can not be zero.')
    return xrange(start + id * step, stop, nthrds * step)


def plist(iter_list):
    l = list(iter_list)
    id = get_thread_num()
    nthrds = get_num_threads()
    return l[id::nthrds]

# lock functions
def init_lock():
    return threading.Lock()


def set_lock(lock):
    lock.acquire()


def unset_lock(lock):
    lock.release()


# helper functions for critical statement
_internal_locks = []


def set_num_of_internal_locks(num):
    global _internal_locks
    _internal_locks = [init_lock() for _ in xrange(num)]


def set_internal_lock(lock_id):
    global _internal_locks
    set_lock(_internal_locks[lock_id])


def unset_internal_lock(lock_id):
    global _internal_locks
    unset_lock(_internal_locks[lock_id])


# helper functions for reduction statement
def reduction_init(op):
    if op == '+':
        return 0
    elif op == '-':
        return 0
    elif op == '*':
        return 1
    elif op == 'max':
        return float('-inf')
    elif op == 'min':
        return float('inf')
    elif op == '&':
        return -1
    elif op == '|':
        return 0
    elif op == '^':
        return 0
    elif op == 'and':
        return True
    elif op == 'or':
        return False


def reduction(op, tot, num):
    if op == '+':
        return tot + num
    elif op == '-':
        return tot - num
    elif op == '*':
        return tot * num
    elif op == 'max':
        return max(tot, num)
    elif op == 'min':
        return min(tot, num)
    elif op == '&':
        return tot & num
    elif op == '|':
        return tot | num
    elif op == '^':
        return tot ^ num
    elif op == 'and':
        return tot and num
    elif op == 'or':
        return tot or num


# helper functions for barrier statement
class _Barrier:
    def __init__(self, n):
        self.n = n
        self.count = 0
        self.mutex = threading.Semaphore(1)
        self.barrier = threading.Semaphore(0)
        self.barrier2 = threading.Semaphore(1)

    def wait(self):
        self.mutex.acquire()
        self.count += 1
        if self.count == self.n:
            self.barrier2.acquire()
            self.barrier.release()
        self.mutex.release()

        self.barrier.acquire()
        self.barrier.release()

        self.mutex.acquire()
        self.count -= 1
        if self.count == 0:
            self.barrier.acquire()
            self.barrier2.release()
        self.mutex.release()

        self.barrier2.acquire()
        self.barrier2.release()


class _Do_Nothing_Barrier:
    def wait(self):
        pass


_barrier = _Do_Nothing_Barrier()


def barrier():
    global _barrier
    _barrier.wait()


# helper functions for dynamic for
_iter_item = None
_loop_lock = init_lock()
def drange(start, stop=None, step=1):
    global _iter_item, _loop_lock
    if stop is None:
        stop = start
        start = 0
    if step == 0:
        raise ValueError('step can not be zero.')
    set_lock(_loop_lock)
    if _iter_item is None:
        _iter_item = start
    unset_lock(_loop_lock)
    while _iter_item < stop:
        set_lock(_loop_lock)
        tmp_iter_item = _iter_item
        _iter_item += step
        unset_lock(_loop_lock)
        if tmp_iter_item >= stop:
            break
        yield tmp_iter_item
    barrier()
    set_lock(_loop_lock)
    if _iter_item is not None:
        _iter_item = None
    unset_lock(_loop_lock)


def dlist(iter_list):
    global _iter_item, _loop_lock
    l = list(iter_list)
    m = len(iter_list)
    set_lock(_loop_lock)
    if _iter_item is None:
        _iter_item = 0
    unset_lock(_loop_lock)
    while _iter_item < m:
        set_lock(_loop_lock)
        tmp_iter_item = _iter_item
        _iter_item += 1
        unset_lock(_loop_lock)
        if tmp_iter_item >= stop:
            break
        yield l[tmp_iter_item]
    barrier()
    set_lock(_loop_lock)
    if _iter_item is not None:
        _iter_item = None
    unset_lock(_loop_lock)


# helper functions for parallel statement
def parallel_run(func, nthrds=None):
    global _barrier
    tmp_num_threads = get_num_threads()
    if nthrds is None or nthrds == 0:
        nthrds = cpu_count()
    set_num_threads(nthrds)
    _barrier = _Barrier(nthrds)
    threads = []
    for i in xrange(get_num_threads()):
        threads.append(threading.Thread(target=func, name=str(i)))
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    set_num_threads(tmp_num_threads)
    _barrier = _Do_Nothing_Barrier()

