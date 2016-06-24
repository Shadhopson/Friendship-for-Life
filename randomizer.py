import numpy as np
p_count = 30
needs_count = []
support_count = []
cost_count = []

for i in range(0,p_count):
    cost_count.append(np.random.normal(0,0.6)*3)

for i in range(0, p_count):
    print np.random.normal(cost_count[i],1)
    needs_count = int(round(np.random.normal(2,0.6) + 0.5*np.random.normal(cost_count[i], 1)))
    if needs_count > 3:
        needs_count = 3
    print needs_count
