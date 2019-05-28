import os
import time
import cv2
import numpy as np

def get_img(rtime):
    video_path = 'short_1car.mp4'  # FPS is about 20, 105 frames in total

    # video_path = os.path.join("videos", "test", video)
    camera = cv2.VideoCapture(video_path)
    # cv2.namedWindow("detection", cv2.WINDOW_AUTOSIZE)

    # Prepare for saving the detected video
    # sz = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
    #     int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    # fourcc = cv2.VideoWriter_fourcc(*'mpeg')

    # vout = cv2.VideoWriter()
    # vout.open(os.path.join("videos", "res", video), fourcc, 20, sz, True)

    img_list = []
    # box_list = []
    # class_list = []
    # score_list = []

    while True:
        res, frame = camera.read()
        img_list.append(frame)

        if not res:
            break
        if cv2.waitKey(110) & 0xff == 27:
                break
    camera.release()
    
    img = img_list[int(rtime*20)%104]
#     print(img.shape)
    
    return img