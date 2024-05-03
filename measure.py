import requests
import threading
import time
import numpy as np
from matplotlib import pyplot as plt

# spawn multiple threads and send http requests to the server
SERVER_IP = '10.129.27.120'
SERVER_PORT = 8887
NUM_THREADS = 100
NUM_ITER = 10

def send_request(page, trigger, json_data):
    # start times and latencies are in nanoseconds
    latencies = []
    start_times = []
    num_failed = 0
    i = 0
    while i < NUM_ITER:
        try:
            json_data['iter'] = i
            start = time.time_ns()
            response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/{page}/{trigger}', json=json_data)
            if response.status_code != 200:
                print(f'Failed')
                num_failed += 1
                continue
            #response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/', json = json_data)
            end = time.time_ns()
            print(f'Sent: {json_data}, Received: {response.text}, latency: {(end - start)/10**6} ms')
            latencies.append((end - start))
            start_times.append(start)
            i += 1
        except:
            num_failed += 1
    return start_times, latencies, num_failed
    
    
# create NUM_THREADS threads
threads = []
for i in range(NUM_THREADS):
    thread = threading.Thread(target=send_request, args=('adi', 'abcd', {'thread': i}))
    threads.append(thread)
    thread.start()

# wait for all threads to finish
res = [threads[i].join() for i in range(NUM_THREADS)]
failed = np.array([r[2] for r in res])
start_times = np.concatenate([r[0] for r in res])
latencies = np.concatenate([r[1] for r in res])
plt.scatter(start_times, latencies)
plt.show()

