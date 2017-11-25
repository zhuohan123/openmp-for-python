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