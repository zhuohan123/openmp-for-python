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

