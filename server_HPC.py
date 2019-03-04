import Streaming
import Segmentation
import Network
import threading
import multiprocessing as mp
import cv2
from time import sleep
def test_server():
	try:
		Tunnel_ = False
		conn,T_thr = Network.set_server(port=6666,Tunnel=Tunnel_,n=1)
		rcv_frames = Streaming.rcv_frames_thread(connection=conn[0])
		send_results = Streaming.send_results_thread(connection=conn[1],scores_f=False)
		while (rcv_frames.isAlive() and send_results.isAlive()):
			frame,status = rcv_frames.get()
			if frame is 0:
				break                
			send_results.put(status=status)
	except (KeyboardInterrupt,IOError,OSError) as e:
		pass
	finally:
		rcv_frames.close()
		send_results.close()
		conn[0].close()
		conn[1].close()
		if Tunnel_:
			T_thr.terminate()
if __name__ == '__main__':
	test_server()
