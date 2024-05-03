import requests
import threading
import time
import numpy as np
from matplotlib import pyplot as plt

# spawn multiple threads and send http requests to the server
SERVER_IP = '10.129.27.120'
SERVER_PORT = 8887
NUM_THREADS = 10
NUM_ITER = 50

BACKOFF = 1
MAX_RESPONSE_WAIT_TIME = 30

SIZE = 100

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
        except requests.exceptions.ConnectionError as e:
            print(e)
            print("Failed 2")
            # num_failed += 1
            time.sleep(BACKOFF)
        except Exception as e:
            print(e)
            print("Failed 3")
            num_failed += 1
    ret[0], ret[1], ret[2] = start_times, latencies, num_failed
    
    
# create NUM_THREADS threads
threads = []
return_vals = [[None]*3 for i in range(NUM_THREADS)]
for i in range(NUM_THREADS):
    thread = threading.Thread(target=send_request, args=('adi', 'cpu-load', {'thread': i, 'size': SIZE}, return_vals[i]))
    threads.append(thread)
    thread.start()

# wait for all threads to finish
for thread in threads:
    thread.join()
try:
    failed = np.array([r[2] for r in return_vals])
    start_times = np.concatenate([r[0] for r in return_vals])
    latencies = np.concatenate([r[1] for r in return_vals])
    print(f'Mean Latency: {latencies.mean()/1e6} ms')
    print(f'Median Latency: {np.median(latencies)/1e6} ms')
    # sort start_times and latencies based on sort_times
    start_times_sorted, sorted_indices = np.sort(start_times), np.argsort(start_times)
    latencies_sorted = latencies[sorted_indices]
    # plt.scatter((start_times-start_times.min())/1e9, latencies/1e6)
    # plt.xlabel('Time (s)')
    # plt.ylabel('Latency (ms)')
    # plt.title('Latency vs Time With Autoscaling')
    # plt.savefig('plots/latency_with_autoscaling_50_warm.png')
    # plt.figure()
    # plt.hist(latencies/1e6, bins=30)
    # plt.xlabel('Latency (ms)')
    # plt.title('Latency Histogram With Autoscaling')
    # # plt.plot((start_times_sorted-start_times_sorted.min())/1e6, latencies_sorted/1e6)
    # plt.savefig('plots/latency_with_autoscaling_hist_50_warm.png')
finally:
    __import__('IPython').embed()
    pass

