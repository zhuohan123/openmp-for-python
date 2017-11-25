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