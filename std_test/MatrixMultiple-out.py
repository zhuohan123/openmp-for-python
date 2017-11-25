import omp
omp.set_num_of_internal_locks(1)
import random
def genMatrix(n):
  _dict1={}
  _dict1['n']=n
  return [random.randrange(_dict1['n']) for i in range(_dict1['n']*_dict1['n'])]
def matrixMul(N, a, b):
  _dict2={}
  _dict2['N']=N
  _dict2['a']=a
  _dict2['b']=b
  _dict2['res'] = [0 for i in range(_dict2['N']*_dict2['N'])]
  # omp parallel num_threads(2) private(n,i,j,tmp,k)
  def _block0():
      # omp for
      for n in omp.prange(_dict2['N']*_dict2['N']):
        i = n / _dict2['N']
        j = n % _dict2['N']
        tmp = 0
        for k in range(_dict2['N']):
        	tmp = tmp + _dict2['a'][i*_dict2['N']+k] * _dict2['b'][k*_dict2['N']+j]
        _dict2['res'][n] = tmp
      omp.barrier()
  # omp parallel end
  omp.parallel_run(_block0,2)
  return _dict2['res']
n = 3
a = genMatrix(n)
b = genMatrix(n)
print a
print b
print matrixMul(n, a, b)
pass

