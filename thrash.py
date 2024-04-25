import requests
import threading
import time

# spawn multiple threads and send http requests to the server
SERVER_IP = '10.129.27.120'
SERVER_PORT = 8887
NUM_THREADS = 10
NUM_ITER = 10

def send_request(page, trigger, json_data):
    for i in range(NUM_ITER):
        json_data['iter'] = i
        start = time.time_ns()
        response = requests.post(f'http://{SERVER_IP}:{SERVER_PORT}/{page}/{trigger}', json=json_data)
        end = time.time_ns()
        print(f'Sent: {json_data}, Received: {response.text}, latency: {end - start} ns')
    
# create NUM_THREADS threads
threads = []
for i in range(NUM_THREADS):
    thread = threading.Thread(target=send_request, args=('mytest', 'test1', {'thread': i}))
    threads.append(thread)
    thread.start()

# wait for all threads to finish
for i in range(NUM_THREADS):
    threads[i].join()