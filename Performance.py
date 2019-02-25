import multiprocessing as mp 
import threading
from queue import Queue
import numpy as np
import time
from collections import deque
def gen_native(i,cond_=threading.Condition(),queue_=deque()):
        n=0
        frame =np.random.randint(low=0,high=2^32-1, size=(1600,900,3))
        for x in range(0,i):
                frame =100; 
                with cond_:
                        queue_.append(frame)
                        cond_.notifyAll()
                        n += 1
        print('\nP1 number of frames generated is',n)
def get_native(i,cond_=threading.Condition(),queue_=deque()):
	n=0
	for x in range(0,i):
		with cond_:
			while not len(queue_):
				cond_.wait()
			y = queue_.popleft()
			n += 1
	print('\nP1 number of frames received is',n)
			
def main_native():
	cond_=threading.Condition()
	queue_=deque()
	T1 = threading.Thread(target=gen_native,args=(10000,cond_,queue_))
	T2 = threading.Thread(target=get_native,args=(10000,cond_,queue_))
	x = time.time()
	T2.start()
	T1.start()
	T1.join()
	T2.join()
	y= time.time()
	print("\nP1",y-x,"sec \n")
	
def gen_queue(i,queue_=Queue()):
        n=0
        frame =np.random.randint(low=0,high=2^32-1, size=(1600,900,3))
        for x in range(0,i):
                queue_.put(frame)
                n += 1
        print('\n P2 number of frames generated is',n)
def get_queue(i,queue_=Queue()):
        n=0
        for x in range(0,i):
                frame = queue_.get()
                #queue_.task_done()
                n +=1
        print('\n P2 number of frames received is',n)
def main_queue():
	queue_=Queue()
	T1 = threading.Thread(target=gen_queue,args=(10000,queue_))
	T2 = threading.Thread(target=get_queue,args=(10000,queue_))
	x = time.time()
	T2.start()
	T1.start()
	T1.join()
	T2.join()
	#queue_.join()
	y= time.time()
	print('\nP2',y-x,"sec")
if __name__ == '__main__':
        P1 = mp.Process(target=main_native,name="P1")
        P2 = mp.Process(target=main_queue,name="P2")
        P1.start()
        P2.start()
        P1.join()
        P2.join()
        time.sleep(10)
