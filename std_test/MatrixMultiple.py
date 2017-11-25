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
