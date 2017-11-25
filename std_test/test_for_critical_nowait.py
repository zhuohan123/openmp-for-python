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