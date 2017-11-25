import matplotlib.pyplot as plt

class MyClass:
    """A simple example class"""
    i = 12345

    def f(self):
        return 'hello world'

def f0():
    def f1():
        pass
    print "hello"

def func(a,b,*d,**e):
    global c,f
    return a+b+c+f

add2 = lambda x,y:x+y

fig, ax = plt.subplots()

graph = open("plot-small.txt")

l = [2*i for i in range(10) if i>0]

i = 1

del i

a = 4
def f():
    a = 2
    def g():
        b = a
        return b
    return g()

cnt = 0
b = 3
(a,b) = (b,a)

def hello_world():
    #omp parallel num_threads(4) private(a,b,c)
    print "hello_world!"
    #omp parallel end
    pass

def hello_world():
    #omp parallel
    print "hello_world!"
    #omp parallel end
    pass

'''
for line in graph.readlines():
    points = list(map(float,line.split(' ')))
    x = [points[0],points[2]]
    y = [points[1],points[3]]
    cnt += 1
    if cnt%100 == 0:
        print(cnt)
    ax.plot(x, y, 'r-')

ax.axis('equal')
plt.show()

graph.close()
'''

def ending():
    pass