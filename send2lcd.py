import time
from threading import Thread
import lcdapi as lcd
import socket
import os

lcd_port = str(lcd.get_port())

os.system("fuser -k "+str(lcd_port))

lcd.init(lcd_port) #Get port and init display
lcd.switch_line(0)
time.sleep(2)
lcd.print_lcd("OS42 Car Display")
time.sleep(4)

callsign = "UNKNOWN"
altitude = 0
temp = 0
time_h = 0
time_m = 0
time_s = 0

counter = 0

def task():
    global counter
    lcd.clear_screen()
    while True:
        counter = counter + 1
        if counter % 5 == 0:
            lcd.clear_screen()
        lcd.switch_line(0)
        lcd.print_lcd(str(callsign)+"    "+str(altitude)+"m")
        lcd.switch_line(1)
        lcd.print_lcd(str(time_h)+":"+str(time_m)+":"+str(time_s)+"  "+str(temp)+"*C")
        time.sleep(1)
    

t1 = Thread(target=task)

t1.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind(('127.0.0.1', 2025))
    s.listen()
    conn, addr = s.accept()

    while True:
        try:
            data = conn.recv(1024)
            data = data.decode()
            print(data)
            if data[0] == "c":
                print("Callsign Packet Received!")
                data = data.split(":")
                callsign = data[1]
            if data[0] == "t":
                print("Temperature Packet Received!")
                data = data.split(":")
                temp = int(data[1])
            if data[0] == "a":
                print("Altitude Packet Received!")
                data = data.split(":")
                altitude = int(float(data[1]))
            if data[0] == "h":
                print("Hour Packet Received!")
                data = data.split(":")
                time_h = int(float(data[1]))
            if data[0] == "m":
                print("Minute Packet Received!")
                data = data.split(":")
                time_m = int(float(data[1]))
            if data[0] == "s":
                print("Second Packet Received!")
                data = data.split(":")
                time_s = int(float(data[1]))
        except KeyboardInterrupt:
            lcd.ser.close()
                    
