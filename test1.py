import time

d = {'qwef':'qwf'}

def func(args):
    print(args)
    time.sleep(1)
    print(d)
    with d['A'].exclusive():
        print('a')
    