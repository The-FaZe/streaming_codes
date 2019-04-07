import Streaming
import Segmentation
import Network
import threading
import multiprocessing as mp
import cv2
from time import sleep
import argparse

parser = argparse.ArgumentParser(description='Online Action Recognition')
parser.add_argument('--p',dest='port',type = int,default =6666)
parser.add_argument('--ip',type=str, default='localhost')
parser.add_argument('--tun',dest = 'tunnel',action='store_true')
parser.add_argument('--rgb',action='store_true')
parser.add_argument('--Ofps',dest= 'old_fps',type= int,default=30)
parser.add_argument('--Nfps',dest= 'new_fps',type= int,default=30)
args = parser.parse_args()
def send_test():
	try:
		id = 0
		capture =Segmentation.Cap_Process(fps_old=args.old_fps,fps_new=args.new_fps,id_=id
			,port=args.port,ip=args.ip,Tunnel=args.tunnel,rgb=False)
		while capture.is_alive():
			frame = capture.get()
			if frame is True :
				break
			cv2.imshow('frame',frame)
			cv2.waitKey(10)
	except (KeyboardInterrupt,IOError,OSError)as e:
		pass
	finally:

		capture.close()
		cv2.destroyAllWindows()
if __name__ == '__main__':
	send_test()
