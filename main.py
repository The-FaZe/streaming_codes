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
p =threading.Thread(target=f,args=(a,))
p.start()
a.put(100)
time.sleep(0.1)
a.put(111)
time.sleep(0.1)
a.put("I'm here")
time.sleep(0.1)
a.close()
p.join()
print("fin")
