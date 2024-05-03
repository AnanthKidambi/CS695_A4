import json
import time
import numpy as np

def handler(request):
    # calculate the inverse of a big matrix
    size = 200
    s = np.linalg.pinv(np.random.rand(size, size))
    request['det'] = np.linalg.det(s)
    request['time'] = time.time()
    return request

if __name__ == "__main__":
    handler({})