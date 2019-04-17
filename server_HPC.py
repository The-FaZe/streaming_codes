from comms_modules.Network import set_server
from comms_modules.Streaming import rcv_frames_thread,send_results_thread
from comms_modules.TopN import Top_N
from numpy.random import random
from random import randint

def test_server():
	try:
		test = True
		Tunnel_ = True
		classInd_file = 'UCF_lists/classInd.txt'
		top5_actions = Top_N(classInd_file)
		conn,T_thr = set_server(port=6666,Tunnel=Tunnel_,n=1)
		rcv_frames = rcv_frames_thread(connection=conn[0])
		send_results = send_results_thread(connection=conn[1],test=test)
		c = 0
		Actf = True 
		while (rcv_frames.isAlive() and send_results.isAlive()):
			frame,status = rcv_frames.get()
			if frame is 0:
				break          
			if c % 10 == 0 and c != 0:
				scores = random(101)
				top5_actions.import_scores(scores)
				index,_,scores = top5_actions.get_top_N_actions()
				Actf = bool(randint(0,1))
				print(Actf)
				send_results.put(status=status,scores=(*index,*scores),Actf=Actf)
			else:
				send_results.put(status=status,Actf=Actf)
			c +=1
	except (KeyboardInterrupt,IOError,OSError) as e:
		pass
	finally:
		rcv_frames.close()
		send_results.close()
		conn[0].close()
		conn[1].close()

if __name__ == '__main__':
	test_server()
