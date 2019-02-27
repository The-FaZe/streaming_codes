import Streaming
import Segmentation
import Network
import threading
import multiprocessing as mp
import cv2
from time import sleep
def test_server():
	try:
		count = 0
		conn,T_thr = Network.set_server(port=6666,Tunnel=True)
		rcv_frames = Streaming.rcv_frames_thread(connection=conn)
		while rcv_frames.isAlive():
			frame = rcv_frames.get()
			if frame is 0:
				break
			count += 1
			#cv2.imshow('frame',frame)
			#cv2.waitKey(30)
		rcv_frames.close()
		T_thr.terminate()
		print("count is",count)
		#cv2.destroyAllWindows()
	except (KeyboardInterrupt,IOError,OSError):
		rcv_frames.close()
		#cv2.destroyAllWindows()
		conn.close()
		T_thr.terminate()
		print("count is",count)
		sleep(3)
if __name__ == '__main__':
	test_server()