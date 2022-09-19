import cv2
import numpy as np
import imutils
from imutils.video import VideoStream
from imutils.video import FPS
import time
import os


CLASSES = ['cardboard', 'glass', 'hard plastics', 'metal', 'paper', 'soft plastics']
RECYCLABLE = [True, True, True, True, True, False]

# opencv DNN
net = cv2.dnn.readNetFromTensorflow("frozen_graph.pb")
# print("OpenCV model was successfully read. Model layers: \n", net.getLayerNames())

vs = VideoStream(src=1).start()
time.sleep(2.0) # warm up camera

fps = FPS().start()

while True:
    # grab the frame from the threaded video stream and resize it to have a maximum width of 400 pixels
    # vs is the VideoStream
    frame = vs.read()
    frame = imutils.resize(frame, width=400)
    h, w = frame.shape[:2]
    input_blob = cv2.dnn.blobFromImage(image=frame, size=(224, 224), swapRB=True,)  # BGR -> RGB
    net.setInput(input_blob)
    # OpenCV DNN inference
    out = net.forward()
    class_id = np.argmax(out)
    confidence = out[0][class_id]

    cv2.imshow("Frame", frame)
    cv2.waitKey(1)
    if confidence > 0.9:
        os.system('clear')
        print("* Class: {}, confidence: {:.4f}".format(CLASSES[class_id], confidence))
        print("* Recyclable: {} \n".format("Yes" if RECYCLABLE[class_id] else "No"))
