#OpenMP for Python

######黎才华，李卓翰

##代码执行方法

1. 进入lib文件夹，使用make命令编译
2. 在主文件夹中对于任意的python程序x.py，可用如下指令生成对应的翻译后的y.py
3. 再在主文件夹下用jython运行y.py即可，测试集在std_test中

~~~bash
./pyomp x.py y.py
~~~


##问题描述

###Python的多线程现状

众所周知，Python语言的多线程并行并不好用。其中的一个原因，就是GIL（Global Interpreter Lock）的影响。这是Python解释器的实现CPython引入的概念。由于CPython的内存管理不是线程安全的，因此CPython引入了一个全局信号量来迫使在同一时间只能有一个线程在运行Python的解释器。因此，Python的多线程 (import threading) 是伪多线程。事实上还会出现多线程跑的比单线程慢的情况。虽然这只是Python的其中一个解释器的问题（如Jython等其他实现就没有这种问题）但由于Cpython的广泛使用，这个问题还是比较严重。

###OpenMP

OpenMP是一种并行程序的编译指导方案，使用Shared Memory Model，支持C/C++/Fortran。简单易用，支持多种并行编程的模型。并且在实现上，OpenMP是先将源代码翻译为对应的Pthreads代码，然后再由一般的编译器进行编译。

###我们的问题

我们的目标是为Python实现一个多线程并行OpenMP，让添加指令后的程序即使在没有OpenMP的情况下也能够被解释执行，即将代码

~~~python
#omp parallel num_threads(8)
print "i love bianyishixi"
#omp parallel end
~~~

转换为

~~~python
def parallel_module():
    print "i love bianyishixi"

threads = []
for i in range(8):
    threads.append(threading.Thread(target=parallel_module))
    threads[i].start()
~~~

然后再将转换后的程序交由非CPython的Python解释（如Jython）执行。

##实现方案

###实现语句总表

~~~python
#omp parallel [end] [num_threads(n)] [private(v1, v2, …)]
#omp for [nowait] [reduction(op : v1, v2, …)] [schedule(dynamic/static)]
#omp sections [end]
  #omp section [end]
#omp critical [end]
#omp barrier

omp.get_thread_num()
omp.get_num_threads()
omp.set_num_threads(n)
~~~

###Parallel语句

我们整个项目的前半期主要都围绕着如何将parallel语句并行化展开的。我们主要利用了Python可以在函数内部定义函数的性质，我们直接在需要并行的代码块处原地定义一个新的函数，然后再在后面补充相应的对于threading库的调用。我们用

~~~python
#omp parallel
#omp parallel end
~~~

分别来表示并行块的开始和结束，则代码

~~~python
def f():
    print "i write dazuoye"
    #omp parallel num_threads(8)
    print "i love bianyishixi"
    #omp parallel end
~~~

将被翻译为

~~~python
def f():
    print "i write dazuoye"
    def parallel_module():
        print "i love bianyishixi"
    threads = []
    for i in range(8):
        threads.append(threading.Thread(target=parallel_module))
    for i in range(8):
        threads[i].start()
~~~

但是这么做会有一个问题：在函数内再定义的函数里被赋值的变量，将会变成新函数的局部变量。如果我们要修改原来函数的局部变量，就必须想办法引用到原先的变量。因此，直接简单的修改会导致变量的作用域发生变化。

由于Python的对象分为可变对象与不可变对象，外层函数的可变对象可以被内层函数所修改，因此我们将一个函数的全部局部变量都存在可变对象里（如一个dictionary中），就可以避免上述问题，例如

~~~python
def f():
    a = 2
    #omp parallel num_threads(8)
    print a
    a = 1
    #omp parallel end
~~~

就可被翻译为

~~~python
def f():
    dic_f[‘a’] = 2
    #omp parallel num_threads(8)
    print dic_f[‘a’]
    dic_f[‘a’] = 1
    #omp parallel end
~~~

但是这样做就意味着我们需要得到原程序中的每一变量具体的作用域，因此我们对整个程序做了语法分析，生成了AST。

由于循环块内部会有局部变量（不在线程间共享），我们实现了private语句，用于指定有哪些变量需要作为私有变量，格式如下

~~~python
#omp parallel private(x, y, z, ...)
~~~


###For语句

对于for语句，我们将对于range/xrange的循环与对一般的列表的分开处理。对于range/xrange的循环，例如：

~~~python
#omp for
for i in xrange(b, e, s):
    dosth
~~~

我们在库中实现了对应的prange(b, e, s)，使得他能够自动根据线程编号来获得其所需要执行的区间所对应的xrange，即将代码翻译成

~~~python
for i in omp.prange(b, e, s):
    dosth
~~~

之后，假设循环的区间为

~~~python
[0, 1, 2, 3]
~~~

则当有两个进程执行时，它们将分别执行

~~~python
0: [0, 2]
1: [1, 3]
~~~

而对于列表的循环，我们实现了对应的plist函数，它使得每个进程来筛出属于自己的部分序列来执行。例如对于循环

~~~python
#omp for
for i in ['x', 'y', 'z', 'w']:
    dosth
~~~

会被翻译为

~~~python
for i in omp.plist(['x', 'y', 'z', 'w']):
    dosth
~~~

则当有两个进程执行时，它们将分别执行

~~~python
0: ['x', 'z']
1: ['y', 'w']
~~~

除了上面的静态调度方式，我们还支持了如下的动态调度方式：

~~~python
#omp for schedule(dynamic)
for i in xrange(n):
    dosth
~~~

在这种情况下，每一个进程会动态的执行每一次循环的任务。当一个进程完成任务之后，它会找到目前最近一个未被完成的任务来执行。

由于循环的特殊性，我们增加了reduction操作：

~~~python
#omp for reduction(+: s)
for i in xrange(n):
    s += i
~~~

它能够使得各个线程间的s互不干扰，然后再在最后做一次reduction操作。具体而言，上述代码将被翻译为

~~~python
for i in xrange(n):
    tmp_s += i
#omp critical
s += tmp_s
#omp critical end
~~~

我们的reduction支持基本上所有的算数运算符，具体有：

~~~python
+, -, *, max, min, &, |, ^, and, or
~~~

###Sections语句

对于如下语句

~~~python
#omp sections
#omp section
A
#omp section end
#omp section
B
#omp section end
#omp sections end
~~~

翻译过后的程序将会使得有两个线程分别执行代码段A与B。

我们考虑将Sections翻译为for循环，再由for语句来完成并行化，即上面的语句将被翻译为

~~~python
#omp for
for i in range(2):
    if i==0:
        A
    elif i==1:
        B
~~~

###Critical语句

critical语句用来确保每条语句在同一时刻只会被一个线程执行，它由用加减锁操作来完成。在翻译源程序时，每碰到一个新的critical语句，分配一个新的全局锁，在代码段前加锁，代码段后解锁。即代码

~~~python
#omp critical
x
#omp critical end
~~~

将被翻译为

~~~python
omp.set_lock()
x
omp.unset_lock()
~~~

###Barrier语句

Barrier语句的形式为

~~~python
#omp barrier
~~~

这条语句会使得在某一时刻，所有较快的进程等待较慢的进程执行到该点后，再统一执行下面的语句。

这一处代码是由三个信号量（mutex）实现的：

~~~python
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
~~~

另外，for、sections后均默认存在一个barrier，For的barrier可显式的由nowait指令取消。

##测试集设计

我们针对不同的目标设计了两类测试集：

1. 第一类测试集是针对不同的OpenMP语句设计测试数据，首先人工比较编译前后的程序是否等价，然后运行程序比较其输出是否合理，以验证编译器的正确性。
2. 第二类测试集主要针对for语句，把OpenMP for Python分别应用到求和问题/求Pi问题问题上，这两个问题是OpenMP应用的最经典的问题，改变线程数，观察程序性能以说明我们的编译器是有效的。

注意：等价性以及正确性的定义是：编译器按OpenMP指令进行编译且运行结果符合编写者的意图，而不完全是编译前后的两个程序输出完全一样（显然不合理且不可能）。

###第一类测试集
第一类测试集主要关注于全面测试已提供的所有语句的正确性，目的在于用最简单易懂的测试样例说明我们的操作是正确的，为此，附上编译前后的代码，以及比较程序的输出结果予以说明。该测试暂时不考虑性能问题，性能问题会在第二类测试集中涉及。

####0.Variable
该测试数据并没有任何OpenMP语句，但其判断变量是否需要替换，以及如何替换，关系重大。基本原则是：global变量不替换，local变量放入dictionary并进行替换，介于local和global的变量按python 3中nonlocal语句的逻辑由内向外找然后替换，特殊的local变量如lambda和comprehension中的以及声明了private的local变量不替换。

编译前：

~~~python
import omp

class MyClass:
    i = 12345
    def f(self):
        return 'hello world'
tmp = MyClass()
print tmp.f()

c = 1
f = 2
def func(a,b,*d,**e):
    global c,f
    return a+b+c+f
print func(3,4,None,None)

add2 = lambda x,y:x+y
print add2(1,2)

l = [2*i for i in range(10) if i>0]
print l

a = 4
def f():
    a = 2
    def g():
        b = a
        return b
    return g()
print f()
~~~

编译后：

~~~python
import omp
omp.set_num_of_internal_locks(0)
class MyClass:
    i = 12345
    def f(self):
        _dict1={}
        _dict1['self']=self
        return 'hello world'
tmp = MyClass()
print tmp.f()
c = 1
f = 2
def func(a,b,*d,**e):
    _dict2={}
    _dict2['a']=a
    _dict2['b']=b
    _dict2['d']=d
    _dict2['e']=e
    global c,f
    return _dict2['a']+_dict2['b']+c+f
print func(3,4,None,None)
add2 = lambda x,y:x+y
print add2(1,2)
l = [2*i for i in range(10) if i>0]
print l
a = 4
def f():
    _dict3={}
    _dict3['a'] = 2
    def g():
        _dict4={}
        _dict4['b'] = _dict3['a']
        return _dict4['b']
    return g()
print f()
pass
~~~

运行结果比较：

编译前：

~~~
hello world
10
3
[2, 4, 6, 8, 10, 12, 14, 16, 18]
2
~~~

编译后：

~~~
hello world
10
3
[2, 4, 6, 8, 10, 12, 14, 16, 18]
2
~~~

####1.	Parallel

Parallel是最基本的语句，如上所述，主要通过新建并行块函数并在末尾用threading多次调用（封装在omp.parallel_run中）以实现多线程。该语句最能体现使用了多线程。编译前：

~~~python
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
~~~

编译后：

~~~python
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
~~~

运行结果比较：

编译前：

~~~
i write dazuoye!!!
0 / 1
i love bianyishixi!
0 / 1
a = 2017
~~~

编译后：

~~~
i write dazuoye!!!
0 / 1
i love bianyishixi!
0 / 4
a = 2017
i love bianyishixi!
1 / 4
 a = 2017
i love bianyishixi!
2 / 4
a = 2017
i love bianyishixi!
3 / 4
a = 2017
~~~

####2.Sections

Sections语句主要利用了下面将要介绍的for语句搭配if语句实现，不需要原地新建函数，与源代码一一对应关系简洁明了。注意默认末尾会添加omp.barrier()（后面将介绍）。

编译前：

~~~python
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
~~~

编译后：

~~~python
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
~~~

运行结果比较：

编译前：

~~~
section 0 from 0
section 1 from 0
~~~

编译后：

~~~
section 0 from 0
section 1 from 1
~~~

####3.For + reduction + dynamic

For+reduction的组合是最常用的语句，也是最能体现并行加速效果的语句，关键在于for的多个循环的如何分配给不同线程（使用plist/dlist/prange/drange），以及reduction时需要加锁。另外，此处需要variable替换策略的一点点配合，也即需要新的临时变量存储每个线程的累加/累乘信息，在最后汇总也需要variable替换策略的配合。

编译前：

~~~python
import omp

num_step = 1000000
step = 1.0 / num_step

def calc_pi_for():
    ans = 0
    # omp parallel num_threads(8) private(i,x)
    # omp for reduction(+:ans) schedule(dynamic)
    for i in range(num_step):
        x = (i + 0.5) * step
        ans += 4.0 / (1.0 + x * x)
    # omp parallel end
    print ans * step

calc_pi_for()
~~~

编译后：

~~~python
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
~~~

运行结果比较：

编译前：

~~~
3.14159265359
~~~

编译后：

~~~
3.14159265359
~~~

####4.	For + critical + nowait

虽然同样在计算pi的问题中，使用reduction减少了使用锁的次数，会比使用critical（每次累加都需要加锁解锁）要好，但该数据只为了呈现critical的作用，关注点在于正确性，暂时不考虑性能问题。

编译前：

~~~python
import omp

num_step = 1000000
step = 1.0 / num_step

def calc_pi_critical():
    ans = 0
    # omp parallel num_threads(8) private(i,x)
    # omp for nowait
    for i in range(num_step):
        x = (i + 0.5) * step
        # omp critical
        ans += 4.0 / (1.0 + x * x)
        # omp critical end
    # omp parallel end
    print ans * step

calc_pi_critical()
~~~

编译后：

~~~python
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
~~~

运行结果比较：

编译前：

~~~
3.14159265359
~~~

编译后：

~~~
3.14159265359
~~~

####5.	Barrier

在输出a和b之间没有barrier，所以a和b理应会混杂着输出，而输出c之前有barrier，所以快的程序会等待慢的程序，然后连续输出c。

编译前：

~~~python
import omp
import time
import random

def barrier_test():
    # omp parallel
    print str(omp.get_thread_num()) + ' a\n',
    time.sleep(random.randrange(3))
    print str(omp.get_thread_num()) + ' b\n',
    time.sleep(random.randrange(3))
    # omp barrier
    print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end

barrier_test()
~~~

编译后：

~~~python
import omp
omp.set_num_of_internal_locks(0)
import time
import random
def barrier_test():
    _dict1={}
    # omp parallel
    def _block0():
        print str(omp.get_thread_num()) + ' a\n',
        time.sleep(random.randrange(3))
        print str(omp.get_thread_num()) + ' b\n',
        time.sleep(random.randrange(3))
        # omp barrier
        omp.barrier()
        print str(omp.get_thread_num()) + ' c\n',
    # omp parallel end
    omp.parallel_run(_block0,0)
barrier_test()
pass
~~~

运行结果比较：

编译前：

~~~
0 a
0 b
0 c
~~~

编译后：

~~~
0 a
1 a
2 a
2 b
3 a
1 b
0 b
3 b
1 c
0 c
3 c
2 c
~~~

####6.	Nowait

该组测试数据比较特殊，需比较是否包含nowait的两组程序的输出，然后才能体现nowait的作用。也即有nowait时，运行得快的程序会先运行程序后面的部分，先输出done，而没有nowait时，运行得快的程序需要等待慢的程序。

带有nowait的：

~~~python
import omp
import time
import random

def nowait_test():
    # omp parallel num_threads(8) private(i)
    # omp for nowait
    for i in range(8):
    	time.sleep(random.randrange(3))
        print str(omp.get_thread_num()) + ' thread\n',
    print "done"
    # omp parallel end

nowait_test()
~~~

不带nowait的：

~~~python
import omp
import time
import random

def nowait_test():
    # omp parallel num_threads(8) private(i)
    # omp for
    for i in range(8):
    	time.sleep(random.randrange(3))
        print str(omp.get_thread_num()) + ' thread\n',
    print "done"
    # omp parallel end

nowait_test()
~~~

运行结果比较：

带有nowait：

~~~
0 thread
done
1 thread
done
3 thread
done
5 thread
done
6 thread
done
2 thread
done
7 thread
done
4 thread
done
~~~

没有nowait：

~~~
2 thread
0 thread
1 thread
3 thread
4 thread
5 thread
6 thread
7 thread
done
done
done
done
done
done
done
done
~~~

####7. MatrixMultiple

除单元测试外，我们也在一般的程序上做了测试，如矩阵乘法就是其中之一，其代码如下：

~~~python
import omp
import random

def genMatrix(n):
  return [random.randrange(n) for i in range(n*n)]

def matrixMul(N, a, b):
  res = [0 for i in range(N*N)]
  # omp parallel num_threads(2) private(n,i,j,tmp,k)
  # omp for
  for n in range(N*N):
    i = n / N
    j = n % N
    tmp = 0
    for k in range(N):
    	tmp = tmp + a[i*N+k] * b[k*N+j]
    res[n] = tmp
  # omp parallel end
  return res

n = 3
a = genMatrix(n)
b = genMatrix(n)
print a
print b
print matrixMul(n, a, b)
~~~

对于较大的n，我们的程序仍能输出正确的结果。

###第二类测试集：

####1.	求和问题测试程序：

~~~python
import omp

def count(n):
    s = 0
    #omp parallel private(i) num_threads(2)
    if omp.get_thread_num()==0:
        print 'num_threads =', omp.get_num_threads()
    #omp for reduction(+:s)
    for i in xrange(n):
        s += i
    #omp parallel end
    return s
print count(500000000)
~~~

令n=500000000，在不同的num\_threads的运行时间如下：

| 线程个数 |  运行时间  |
| :--: | :----: |
|  1   | 20.10s |
|  4   | 9.17s  |

####2.	求pi问题测试程序：

~~~python
import omp

num_step = 300000000
step = 1.0 / num_step

def calc_pi_for():
    ans = 0
    # omp parallel num_threads(2) private(i,x)
    # omp for reduction(+:ans)
    for i in xrange(num_step):
        x = (i + 0.5) * step
        ans += 4.0 / (1.0 + x * x)
    # omp parallel end
    print "%.10f\n" % (ans * step),

calc_pi_for()
~~~

令num\_step=300000000，运行时间随num\_threads的变化如下：

| 线程个数 |  运行时间  |
| :--: | :----: |
|  1   | 10.57s |
|  4   | 4.99s  |

##完成情况与存在的问题

我们完成了开题报告中的全部目标。但我们的项目仍存在一些问题：

- 鲁棒性不是很强，对于不标准的python代码支持不好
  - 如缩进使用tab的代码
- 原理上的问题
  - 没有从根本上解决GIL的问题，Jython的通用性、对三方库的支持、以及效率都不能达到CPython的水准

##致谢
- 感谢所有成员的付出与合作
- 感谢老师和助教的指导
- 感谢其他同学的建议与支持
