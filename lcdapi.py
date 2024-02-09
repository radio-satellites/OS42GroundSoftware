import serial
import time
import sys
import glob

def get_port():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result[0]


def init(port):
    global ser
    ser = serial.Serial(port,115200)
    time.sleep(0.05) #Wait for things to settle
    print("Using port "+str(ser.portstr))
    
def print_lcd(string):
    ser.write(string.encode())
    
def switch_line(line):
    if line == 1:
        ser.write(b">")
    elif line == 0:
        ser.write(b"<")
def clear_screen():
    ser.write(b"%")

def deinit():
    ser.close()         

