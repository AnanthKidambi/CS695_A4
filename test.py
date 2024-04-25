from multiprocessing import Manager, Process
from test1 import func, d
from multiprocessing_utils import SharedRLock 

if __name__ == "__main__":
    manager = Manager()
    access_times_dict = manager.dict()
    p = Process(target=func, args=(access_times_dict,))
    d['A'] = SharedRLock()
    access_times_dict['qwefn'] = 'qwef'
    p.start()
    p.join()