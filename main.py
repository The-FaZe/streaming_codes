import threading
import time
def f(a):
	print('start')
	while True:
		b=a.get()
		print(b)
		if b == 0:
			break
from comms_modules.Segmentation import thrQueue
a = thrQueue()
b = thrQueue()
inpa = list(range(1,101))
inpa.append(0)
inpb = list(range(101,201))
inpb.append(0)
list(map(lambda x: a.put(x), inpa)) 
list(map(lambda x: b.put(x), inpb)) 
p =threading.Thread(target=f,args=(a,))
p.start()
f(b)