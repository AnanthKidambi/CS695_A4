import json
import time
import math

def handler(request):
    with open('/out.log', 'w') as f:
        f.write(f"Received request: {json.dumps(request)}")
        f.write(f"time: {time.time()}")
    i = 1
    for i in range(100000):
        i = math.cos(i) 
    return request
