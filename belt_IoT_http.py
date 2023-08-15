import cv2
import numpy as np
from RPLCD import i2c
import RPi.GPIO as GPIO
import time 
import requests

# Set up GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.IN)
GPIO.setup(37, GPIO.OUT)
GPIO.output(37, 1)
GPIO.setup(19, GPIO.IN)
servo = GPIO.PWM(11, 50)
servo.start(0)
duty = 2

# Set up camera
cap = cv2.VideoCapture(0)

# Set up LCD
lcdmode = 'i2c'
cols = 16
rows = 2
charmap = 'A00'
i2c_expander = 'PCF8574'
address = 0x27
port = 1
lcd = i2c.CharLCD(i2c_expander, address, port=port, charmap=charmap,
                  cols=cols, rows=rows)

# Define ThingSpeak parameters
API_KEY = 'YOUR_API_KEY'  # Replace with your ThingSpeak API Key
CHANNEL_ID = 'YOUR_CHANNEL_ID'  # Replace with your ThingSpeak Channel ID
FIELD_ID = 'YOUR_FIELD_ID'  # Replace with your ThingSpeak Field ID

# Function to publish data to ThingSpeak
def publish_to_thingspeak(area):
    url = f'https://api.thingspeak.com/update?api_key={API_KEY}&field{FIELD_ID}={area}'
    response = requests.get(url)
    if response.status_code == 200:
        print("Data published to ThingSpeak successfully!")
    else:
        print("Failed to publish data to ThingSpeak.")

while True:
    _, frame = cap.read()

    # Belt
    cv2.imshow("frame", frame)
    belt = frame[180: 327, 150: 500]
    framecenter = int(147 / 2)
    
    gray_belt = cv2.cvtColor(belt, cv2.COLOR_BGR2GRAY)
    _, threshold = cv2.threshold(gray_belt, 200, 255, cv2.THRESH_BINARY)
    cv2.line(belt, (0, framecenter), (350, framecenter), (0, 0, 0), 2)

    # Read sensor values
    sensor1 = GPIO.input(13)
    if sensor1 == 1:
        count_overall += 1
        time.sleep(0.5)

    sensor2 = GPIO.input(19)
    if sensor2 == 1:
        count_required_size += 1
        time.sleep(0.5)

    # Detect the Nuts
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for cnt in contours:
        (x, y, w, h) = cv2.boundingRect(cnt)
        sub = framecenter - y
        if sub <= 20:
            sol = cv2.contourArea(cnt) / 600
            
    if sol > 0.5:
        area = round(sol, 2)
        if area < 0.5:
            servo.ChangeDutyCycle(8.3)
            publish_to_thingspeak(area)
            
    if area > 1:
        cv2.rectangle(belt, (x, y), (x + w, y + h), (0, 0, 255), 2)
        servo.ChangeDutyCycle(2.3)
        cv2.putText(belt, str(area), (x, y), 1, 1, (0, 255, 0))
        if area < 0.5:
            servo.ChangeDutyCycle(8.3)
            publish_to_thingspeak(area)

    if 0.5 <= area < 1:
        cv2.rectangle(belt, (x, y), (x + w, y + h), (255, 0, 0), 2)
        servo.ChangeDutyCycle(8.5)
        cv2.putText(belt, str(area), (x, y), 1, 1, (0, 255, 0))
        if area < 0.5:
            servo.ChangeDutyCycle(4.5)
            publish_to_thingspeak(area)

    data = "Area is " + str(area) + " cm^2"
    lcd.cursor_pos = (0, 0)
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
