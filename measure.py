import requests
import threading
import time
import numpy as np
from matplotlib import pyplot as plt

# spawn multiple threads and send http requests to the server
SERVER_IP = '10.129.27.120'
SERVER_PORT = 8887
NUM_THREADS = 10
NUM_ITER = 20

BACKOFF = 1
MAX_RESPONSE_WAIT_TIME = 30

def send_request(page, trigger, json_data, ret):
    # start times and latencies are in nanoseconds
    latencies = []
    start_times = []
    num_failed = 0
    i = 0
    while i < NUM_ITER:
        try:
            json_data['iter'] = i
            start = time.time_ns()
            response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/{page}/{trigger}', json=json_data, timeout=MAX_RESPONSE_WAIT_TIME)
            if response.status_code != 200:
                print(f'Failed')
                num_failed += 1
                time.sleep(BACKOFF)
                continue
            #response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/', json = json_data)
            end = time.time_ns()
            print(f'Sent: {json_data}, Received: {response.text}, latency: {(end - start)/10**6} ms')
            latencies.append((end - start))
            start_times.append(start)
            i += 1
        except Exception as e:
            print(e)
            print("Failed 2")
            num_failed += 1
            time.sleep(BACKOFF)
    ret[0], ret[1], ret[2] = start_times, latencies, num_failed
    
    
# create NUM_THREADS threads
threads = []
return_vals = [[None]*3 for i in range(NUM_THREADS)]
for i in range(NUM_THREADS):
    thread = threading.Thread(target=send_request, args=('adi', 'cpu-load', {'thread': i, 'size': 10}, return_vals[i]))
    threads.append(thread)
    thread.start()

# wait for all threads to finish
for thread in threads:
    thread.join()
try:
    failed = np.array([r[2] for r in return_vals])
    start_times = np.concatenate([r[0] for r in return_vals])
    latencies = np.concatenate([r[1] for r in return_vals])
    # sort start_times and latencies based on sort_times
    start_times_sorted, latencies_sorted = zip(*sorted(zip(start_times, latencies)))
    start_times_sorted, latencies_sorted = np.array(start_times), np.array(latencies)
    # plt.scatter((start_times-start_times.min())/1e6, latencies/1e6)
    plt.plot((start_times_sorted-start_times_sorted.min())/1e6, latencies_sorted/1e6)
    plt.savefig('plots/latency.png')
finally:
    __import__('IPython').embed()

