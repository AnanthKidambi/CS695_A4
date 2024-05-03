import json
import time
import threading

def write_data(num_writes, thread_id, data):
    with open(f'/home/data_{thread_id}.txt', 'w') as f:
        for _ in range(num_writes):
            f.write(data)
            f.flush()

def handler(request):
    # calculate the inverse of a big matrix
    num_writes = 100
    num_threads = 10
    data = 'data'
    if 'num_writes' in request:
        num_writes = int(request['num_writes'])
    if 'num_threads' in request:
        num_threads = int(request['num_threads'])
    if 'data' in request:
        data = request['data']
    threads = []
    for i in range(num_threads):
        threads.append(threading.Thread(target=write_data, args=(num_writes, i, data)))
    for i in range(num_threads):
        threads[i].start()
    for i in range(num_threads):
        threads[i].join()
    request['time'] = time.time()
    return request
    
if __name__ == "__main__":
    handler({'num_writes':100, 'num_threads':10, 'data':'data'})
