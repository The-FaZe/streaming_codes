import Streaming
import Segmentation
import Network
import threading
import multiprocessing as mp
import cv2
from time import sleep
def send_test():
	try:
		capture =Segmentation.Cap_Process(fps_old=8,fps_new=6,id_=0
			,port=6666,ip="192.168.1.112",Tunnel=False,rgb=False)
		while capture.is_alive():
			frame = capture.get()
			if frame is True :
				break
			cv2.imshow('frame',frame)
			cv2.waitKey(30)
		capture.close()
		cv2.destroyAllWindows()
	
	except (KeyboardInterrupt,IOError,OSError):
		capture.close()
		cv2.destroyAllWindows()
if __name__ == '__main__':
	send_test()
