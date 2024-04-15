import json
import time

def handler(request):
    with open('/out.log', 'w') as f:
        f.write(f"Received request: {json.dumps(request)}")
        f.write(f"time: {time.time()}")
    return request