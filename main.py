from comms_modules.Segmentation import thrQueue
import threading
import cv2
import subprocess as sp
import numpy as np
import os

capture = cv2.VideoCapture(0)
ret, frame = capture.read()
height, width, ch = frame.shape
ffmpeg = 'FFMPEG'
dimension = '{}x{}'.format(width, height)
print(dimension)
f_format = 'bgr24'
fps = str(8)
command = [ffmpeg,
		'-y',
		'-f', 'rawvideo',
		'-vcodec','rawvideo',
		'-s', dimension,
		'-pix_fmt', 'bgr24',
		'-r', fps,
		'-i', '-',
		'-an',
		'-c:v', 'libx264',
		'-preset','slow',
		'-crf','30',
		'-f','h264',
		'-'
    	]
command2=[ffmpeg,
		'-f','h264',
		'-i', '-',
		'-f', 'rawvideo',
		'-vcodec','rawvideo',
		'-pix_fmt', 'bgr24',
		'-hide_banner',
		'-'
		]
counter = 0
c = 0
c1 = 0 
frames = []
while True:
	success, frame = capture.read()
	if not success:
		break
	c += 1
	cv2.imshow('capture', frame)
	if counter == 0:
		proc = sp.Popen(command, stdin=sp.PIPE, stderr=sp.PIPE,stdout=sp.PIPE,shell=True,bufsize=10**8)
		proc.stdin.write(frame.tostring())
		counter += 1
	elif counter <= 4:
		proc.stdin.write(frame.tostring())
		counter += 1
	else: 
		stdout=proc.communicate(frame.tostring())[0]
		counter = 0 
		proc2 = sp.Popen(command2, stdin=sp.PIPE, stderr=sp.PIPE,stdout=sp.PIPE,shell=True,bufsize=10**8)
		stdout=proc2.communicate(stdout)[0]
		it = len(stdout)//(480*640*3)
		for i in range(it):
			frame =  np.frombuffer(stdout[480*640*3*i:480*640*3*(i+1)], dtype='uint8')
			frame=frame.reshape((480,640,3))
			cv2.imshow('decoded', frame)
			frames.append(frame)
			c1 += 1

	if cv2.waitKey(5) & 0x3f == ord('q') & 0x3f:
		print(c1,c)
		break
if proc.poll() == None:
	proc.terminate()
