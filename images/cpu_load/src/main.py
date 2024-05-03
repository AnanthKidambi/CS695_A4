import json
import time
import numpy as np

def handler(request):
    # calculate the inverse of a big matrix
    size = 200
    if 'size' in request:
        size = int(request['size'])
        print(size)
    s = np.linalg.pinv(np.random.rand(size, size))
    request['det'] = np.linalg.det(s)
    request['time'] = time.time()
    request['size'] = size
    return request

if __name__ == "__main__":
    handler({'size':10})
