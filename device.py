import socket
import sys

import random
import numpy as np

import time

import pickle

from detection import *
from get_img import *
# import cv2




def socket_client(test_mode = 0):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 6666))
    except socket.error as msg:
        print (msg)
        sys.exit(1)
    print (s.recv(1024).decode())


    #############################################
    ###############loading Yolo Module###########
    yolo, all_classes = load_yolo_model()
    #############################################
    #############################################
    
    start_time = time.time()
    while 1:
        # keep sending events to server at 1 Hz frequency
        while True:
            
            sleep_time = 0.5
            time.sleep(sleep_time)
            
            # sending object detection result as events
            # events: [ event_type/obj, event_sid, event_time ]
            
            # fetching image at 2 HZ from a video footage (20fps)
#             image_path = 'cam1.jpg'
#             camera_img = cv2.imread(image_path)
            
            event_time = time.time()-start_time
            event_sid = 0
            camera_img = get_img(event_time)
            event_obj = object_detector(camera_img, yolo, all_classes)

            event = [event_obj, event_sid, event_time]
            

            print("sending: ", event)
            data=pickle.dumps(event)
            s.send(data)
    
        if data == 'exit':
            break
    s.close()


if __name__ == '__main__':
    socket_client(test_mode = 1)
