import numpy as np

l = [1, 2, 2, 3, 3, 4]
l_np = np.array(l)

percentiles = np.percentile(l, q=[25, 50, 75])
print ['1', '2'] + map(str, percentiles)