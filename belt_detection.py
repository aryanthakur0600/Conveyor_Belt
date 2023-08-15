import cv2
import numpy as np
from RPLCD import i2c
import RPi.GPIO as GPIO
import time 
import argparse
import imutils
import numpy as np
import os
import math
count_required_size=0
count_smaller=0
count_overall=0
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.IN)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37,1)
GPIO.setup(19, GPIO.IN)
duty = 2
area=0
sol=0
cap = cv2.VideoCapture(0)
currentframe=0
lcdmode = 'i2c'
cols = 16
rows = 2
charmap = 'A00'
i2c_expander = 'PCF8574'
address = 0x27
port = 1
lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

while True:
    _, frame = cap.read()

    # Belt
    
    cv2.imshow("frame",frame)
    belt = frame[180: 327, 150: 500]
   
    framecenter=int(147/2)
    
    gray_belt = cv2.cvtColor(belt, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray_belt, 140, 255, cv2.THRESH_BINARY)
    cv2.line(belt,(0,framecenter),(350,framecenter),(0,0,0),2)
    
    # Detect the Nuts
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        sub=framecenter-y
        if sub<=20:
            sol = cv2.contourArea(cnt) / 670
        
            
    if sol > 0.5:
        area = round(sol, 1)
    if area > 1:
        
        cv2.rectangle(belt, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.putText(belt, str(area), (x, y), 1, 1, (0, 255, 0))
      

    if 0.5 <= area <1:
        
        cv2.rectangle(belt, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(belt, str(area), (x, y), 1, 1, (0, 255, 0))
        


    data = "Area is" + " " + str(area) + "cm^2"
    lcd.cursor_pos=(0,0)
    lcd.write_string(data)
    lcd.crlf()
    lcd.close(clear=True)
    cv2.imshow("belt", belt)
    cv2.imshow("threshold", threshold)
    key = cv2.waitKey(1)
    if key == 27:
        break
cap.release()
cv2.destroyAllWindows()
