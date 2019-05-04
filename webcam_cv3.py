import cv2
import sys
import logging as log
import datetime as dt
from time import sleep
import statistics
import wmi
import win32api

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
log.basicConfig(filename='webcam.log',level=log.INFO)

video_capture = cv2.VideoCapture(0)
anterior = 0
i = 0
faceAreaSamples = []
debugN = 10
c = wmi.WMI(namespace='wmi')
b = c.WmiMonitorBrightness()[0]
startingBrightness = b.CurrentBrightness

brightnessMethods = c.WmiMonitorBrightnessMethods()[0]

while True:
    if not video_capture.isOpened():
        print('Unable to load camera.')
        sleep(5)
        pass

    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30)
    )

    if len(faces) == 1:
        i = i + 1
        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            print(i," ",h*w)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    if anterior != len(faces):
        anterior = len(faces)
        log.info("faces: "+str(len(faces))+" at "+str(dt.datetime.now()))


    # Display the resulting frame
    cv2.imshow('Video', frame)

    if i < 5*debugN:
        for (x,y,h,w) in faces:
            faceAreaSamples.append(h*w/1000) 
    else:
        if i > 5*debugN:
            #check stuff
            if h*w/1000 > mean + stdev*3:
                #alert
                print("too close")
                brightnessMethods.WmiSetBrightness(25, 0)
                win32api.MessageBox(0,"You are too close to screen","Warning")
                brightnessMethods.WmiSetBrightness(startingBrightness, 0)
        else:
            mean = statistics.mean(faceAreaSamples)
            stdev = statistics.stdev(faceAreaSamples)
            print("calibration complete ","mean:",mean," stdev:",stdev)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)
    sleep(1/debugN)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
