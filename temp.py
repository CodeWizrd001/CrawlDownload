from multiprocessing import Process, Queue

import time

def print_nums(n) :
    for i in range(n*100,n*100+100) :
        print(i)

processes = []

if __name__ == '__main__' :
    for i in range(2) :
        p = Process(target=print_nums, args=(i,))
        p.start()
        processes.append(p)

    for p in processes :
        p.join()