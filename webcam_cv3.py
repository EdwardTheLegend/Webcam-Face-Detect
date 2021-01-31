import cv2
from time import sleep
import statistics
import wmi
import tkinter as tk

cascade_path = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascade_path)

video_capture = cv2.VideoCapture(0)
anterior = 0
i = 0
face_area_samples = []
sleep_time = 10
calibration_times = 10
c = wmi.WMI(namespace='wmi')
b = c.WmiMonitorBrightness()[0]
starting_brightness = b.CurrentBrightness

brightness_methods = c.WmiMonitorBrightnessMethods()[0]


class Reminder(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.overrideredirect(True)
        tk.Label(self, text="Too close to the screen").grid(row=0, column=0)
        tk.Button(self, command=self.destroy, text="OK").grid(row=1, column=0)
        self.lift()  # Puts Window on top
        self.grab_set()  # Prevents other Tkinter windows from being used


def show_reminder():
    Reminder()

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
        i += 1
        for (x, y, width, height) in faces:
            print(i, " ", height*width)
            cv2.rectangle(frame, (x, y), (x+width, y+height), (0, 255, 0), 2)

    if anterior != len(faces):
        anterior = len(faces)

    cv2.imshow('Video', frame)

    if i == calibration_times:
        mean = statistics.mean(face_area_samples)
        stdev = statistics.stdev(face_area_samples)
        print("calibration complete ", "mean:", mean, " stdev:", stdev)
    elif i < calibration_times:
        for (x, y, height, width) in faces:
            face_area_samples.append(height*width/1000)
    elif i > calibration_times:
        if height*width/1000 > mean + stdev*3:
            print("too close")
            brightness_methods.WmiSetBrightness(25, 0)
            show_reminder()
            brightness_methods.WmiSetBrightness(starting_brightness, 0)
    else:
        raise ValueError

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    # Display the resulting frame
    cv2.imshow('Video', frame)
    sleep(sleep_time)

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
