import numpy as np

def time_emission(pr: tuple, tr: float, path: tuple, c: float=343.0, epsilon: float=1e-12) -> float:
    
    pr = np.array(pr, dtype=float)
    
    for path_index in range(len(path)-1):

        a = path[path_index]
        b = path[path_index+1]

        t0 = a[0]
        t1 = b[0]

        p0 = np.array(a[1], dtype=float)
        p1 = np.array(b[1], dtype=float)

        v = (p1-p0)/(t1-t0)

        if t0 <= tr:
            
            d0 = pr - p0

            A = np.dot(v, v) - c**2
            B = 2 * (c**2 * (tr - t0) - np.dot(d0, v))
            C = np.dot(d0, d0) - (c * (tr - t0))**2


            if abs(A) < epsilon:
                if abs(B) < epsilon:
                    if abs(C) < epsilon:
                        raise Exception("infinite values")
                else:
                    te = -C/B + t0
                    if t0 <= te < t1 and te <= tr+epsilon:
                        return te, p0+v*te
            else:
                delta = B**2 - 4*A*C
                if abs(delta) < epsilon:
                    te = -B/(2*A)
                    if t0 <= te < t1 and te <= tr+epsilon:
                        return te, p0+v*te
                elif delta > 0:
                    sqrt_delta = np.sqrt(delta)
                    te = min((-B - sqrt_delta) / (2*A) + t0, (-B + sqrt_delta) / (2*A) + t0)
                    if t0 <= te < t1 and te <= tr+epsilon:
                        return te, p0+v*te

    return None, None
