import PySimpleGUI as sg
import constants
import PacketHandler42 as packets
import socket
import psutil
import platform
import time
from PIL import Image
import os
import pyperclip
import subprocess
from subprocess import Popen, PIPE
from sondehub.amateur import Uploader
import sondehub_config as config
import datetime
import iconfile

version = "0.9.1"

initial = True #First time through

callsign_good = False
callsign_dec = ""

reading = -9

spacecraft_names = ['OS42','OS42-T','OS42-3','OS42-4','OS42-5']

spacecraft = spacecraft_names[0] #Default spacecraft to receive

TCP_IP = '127.0.0.1'
TCP_PORT = 2000
BUFFER_SIZE = 1024

imagery_buffer = bytearray()

imagery_count = 0
gps_count = 0
uk_count = 0
total_count = 0
kb_count = 0

image_count = 0

isSSDV = True

try:

    f_imageid = open("imageid.txt",'r')
    image_count = int(f_imageid.read())
    print("Recovered progress at image "+str(image_count))
except FileNotFoundError:
    f_imageid = open("imageid.txt",'w')
    f_imageid.write("0")
    f_imageid.close()

previous_imageid = 0
imageid_now = 0


col2 = sg.Column([[sg.Frame('Socket/Telemetry stats:', [[sg.Text("Socket Disconnected",text_color="red",key="-SOCKETTEXT-")],[sg.Text("Total KB downlinked: N/A",key="-TOTALKBTEXT-")],[sg.Text("Imagery Frames: N/A",text_color="green",key="-IMAGERYCOUNTTEXT-")],[sg.Text("GPS/Telemetry Frames: N/A",text_color="orange",key="-GPSFRAMETEXT-")],[sg.Text("Unknown Frames: N/A",text_color="red",key="-UNKNOWNTEXT-")],[sg.Text("Total Frames: N/A",key="-TOTALFRAMETEXT-")],[sg.Button("Flush all imagery",key="-IMGFLUSH-")],[sg.Button("Copy GPS coordinates",key="-COPYCOORDS-")]])],
                  [sg.Frame('Spacecraft Telemetry/Stats:',
                            [[sg.Text("Spacecraft Name: N/A",key="-SPACECRAFTNAME-")],[sg.Text("Latitude: N/A",key="-LATTEXT-")],[sg.Text("Longitude: N/A",key="-LONGTEXT-")],[sg.Text("Altitude: N/A",key="-ALTITUDETEXT-")],[sg.Text("Speed: N/A",key="-SPEEDTEXT-")],[sg.Text("Temperature: N/A",key="-TEMPTEXT-")],[sg.Text("Timestamp: N/A",key="-TIMETEXT-")]])],
                  [sg.Frame('Spacecraft:', [[sg.Listbox(spacecraft_names, default_values=spacecraft_names[0], size=(20, 4), enable_events=True, key='-SPACECRAFTLIST-')],])],
                  [sg.Frame('Spacecraft/Ground station syslog:', [[sg.Column([[sg.Multiline(size=(60,15), font='Courier 8', expand_x=True, expand_y=True, write_only=True,
                                    reroute_stdout=True, reroute_stderr=True, echo_stdout_stderr=True, autoscroll=True, auto_refresh=True)]],pad=(0,0))]])]])

col1 = sg.Column([
    [sg.Frame('Spacecraft Imagery:', [[sg.Text(), sg.Column([[sg.Image("default.png",key='-IMAGE-'),],], size=(670,510), pad=(0,0))]])], ], pad=(0,0))

# The final layout is a simple one
layout = [[col1, col2]]

window = sg.Window('OS-42 Dashboard', layout,icon=iconfile.window_icon)

#Create directory for our images

os.system("mkdir rx")


def updateFigures():
    window[constants.TOTAL_KB_DOWNTEXT].update("Total KB downlinked: "+str(round(kb_count/1000,1)))
    window[constants.IMAGEPACKET_TEXT].update("Imagery Frames: "+str(imagery_count))
    window[constants.GPSPACKET_TEXT].update("GPS/Telemetry Frames: "+str(gps_count))
    window[constants.UNKNOWNFRAME_TEXT].update("Unknown Frames: "+str(uk_count))
    window[constants.TOTALFRAME_TEXT].update("Total Frames: "+str(total_count))

"""
def paste(str, p=True, c=True):
    

    if p:
        p = Popen(['xsel', '-pi'], stdin=PIPE)
        p.communicate(input=str)
    if c:
        p = Popen(['xsel', '-bi'], stdin=PIPE)
        p.communicate(input=str)

"""

while True:
    event, values = window.read(timeout=1) #Run every 1ms
    if initial:
        #This is the first time we are in this loop
        uname = platform.uname()
        
        print("=========OS-42 Dashboard=========")
        print("Written by Sasha VE3SVF")
        print(f"System: {uname.system}")
        print(f"Node Name: {uname.node}")
        print(f"Release: {uname.release}")
        print(f"Version: {uname.version}")
        print(f"Machine: {uname.machine}")
        print(f"Processor: {uname.processor}")
        print("=================================")

        print("")

        print("Selected default spacecraft "+str(spacecraft))

        window[constants.SPACECRAFT_TEXT].update("Spacecraft Name: "+str(spacecraft))

        print("Starting Sondehub uploader...")

        sondehub_enabled = False

        try:

            uploader = Uploader(
            config.CALLSIGN,
            uploader_position=[config.LAT, config.LONG, config.ALT], # [latitude, longitude, altitude]
            uploader_radio = config.RADIO, # Radio information - Optional
            uploader_antenna = config.ANTENNA, # Antenna information - Optional
            developer_mode = config.ENABLE_DEV,
            software_name = "OS-42 Dashboard",
            software_version = version
            )

            #Upload station position

            uploader.upload_station_position(
            config.CALLSIGN,
            [config.LAT, config.LONG, config.ALT], # [latitude, longitude, altitude]
            uploader_radio=config.RADIO, # Radio information - Optional
            uploader_antenna=config.ANTENNA # Antenna information - Optional
            )

            sondehub_enabled = True

            print("Success!")
        except:
            print("Failed!")

        socket_connected = False
        
        while socket_connected == False:
        
            print("Attempting to connect to socket...")

            window[constants.SOCKET_TEXT].update("Connecting...",text_color="orange")
            
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                s.connect((TCP_IP, TCP_PORT))
                #s.settimeout(1)
                
                print("Success!")
                window[constants.SOCKET_TEXT].update("Socket Connected",text_color="green")
                socket_connected = True

                #Update more GUI

                window[constants.TOTAL_KB_DOWNTEXT].update("Total KB downlinked: "+str(round(kb_count/1000,1)))
                window[constants.IMAGEPACKET_TEXT].update("Imagery Frames: "+str(imagery_count))
                window[constants.GPSPACKET_TEXT].update("GPS/Telemetry Frames: "+str(gps_count))
                window[constants.UNKNOWNFRAME_TEXT].update("Unknown Frames: "+str(uk_count))
                window[constants.TOTALFRAME_TEXT].update("Total Frames: "+str(total_count))
            except Exception as e:
                print("Failed!")
                print(e)
                window[constants.SOCKET_TEXT].update("Socket Disconnected",text_color="red")
                time.sleep(1)

        initial = False
        print("Waiting for packets...")

    if initial == False:
        #Be REALLY sure we're not starting for the first time...
        #Read some data
        try:
            if isSSDV:
                start_time = time.time()
            else:
                isSSDV = True
            data = s.recv(BUFFER_SIZE)
        except Exception as e:
            print(e)
            socket_connected = False
            start_time = time.time()
            initial = True #Go back to the connection stage and restart the application
        
        packet_type = packets.get_packet_type(data) #Get packet type

        if packet_type == packets.OS42_TYPE_IMAGERY:
            imagery_count = imagery_count+1
            total_count = total_count + 1
            kb_count = kb_count + 255
            updateFigures()
            #print(time.time() - start_time)

            if time.time() - start_time > 1.5:
                #New image, save the previous one and move on
                #Redecode everything
                return_code,imageid = packets.decode_ssdv(imagery_buffer,spacecraft)
                #Move our temp file into a safe place
                os.rename(os.getcwd()+"/rxtemp.ssdv", os.getcwd()+"/rx/rxtemp.ssdv")
                os.rename(os.getcwd()+"/rxtemp.jpg", os.getcwd()+"/rx/rxtemp.jpg")
                #Rename our files
                os.rename(os.getcwd()+"/rx/rxtemp.ssdv", os.getcwd()+"/rx/"+str(image_count)+".ssdv")
                os.rename(os.getcwd()+"/rx/rxtemp.jpg", os.getcwd()+"/rx/"+str(image_count)+".jpg")

                #Initiate the camera post processing script
                process = subprocess.Popen(['python3',os.getcwd()+'/correct.py',str(os.getcwd()+"/rx/"+str(image_count)+".jpg"),str(os.getcwd()+"/rx/"+str(image_count)+"_corr.png")])

                #Now, prepare for the new image
                imagery_buffer = bytearray(data)
                previous_imageid = imageid_now

                image_count = image_count + 1

                f_imageid = open("imageid.txt",'w')
                f_imageid.write(str(image_count))
                f_imageid.close()
                
                print("Finished downlinking image with Image ID "+str(imageid_now)+" with local ID "+str(image_count-1))
            else:
                imagery_buffer = imagery_buffer + data

            if total_count % 4 == 0:
                #Decode SSDV
                try:
                    return_code,imageid = packets.decode_ssdv(imagery_buffer,spacecraft)
                    if return_code == packets.OS42_TYPE_SUCCESS:
                        callsign_dec = spacecraft
                        callsign_good = True
                except:
                    imageid = -2
                    return_code = -4
                imageid_now = imageid
                
                if return_code == packets.OS42_TYPE_SUCCESS:
                    im = Image.open('rxtemp.jpg')
                    im.save('rxtemp.png')
                    window[constants.SSDV_IMAGE].update("rxtemp.png")
        elif packet_type == packets.OS42_TYPE_GPS_LOCK:
            print("[TLM] High speed telemetry GPS lock")
            gps_count = gps_count + 1
            updateFigures()
            
            isSSDV = False
        elif packet_type == packets.OS42_TYPE_GPS:
            #This is a GPS packet
            try:
                success, alt, lat, long, frame_id,speed_ms,h_t,m_t,s_t = packets.decode_GPS(data)
            except:
                print("Unable to decode GPS packet.")
                pass
            
            if success == packets.GPS_FRAME_VALID:
                f = open("GPSLog.txt",'a')
                try:
                    f.write(data.decode()+"\n")
                except:
                    pass
                f.close()
                
                #GPS frame is valid!
                print("New extended GPS frame")
                print("========================")
                print("Frame number "+str(frame_id))
                print("")
                print("Latitude: "+str(lat))
                print("Longitude: "+str(long))
                print("Altitude: "+str(alt))
                print("GPS string:")
                print(str(lat)+","+str(long))
                print("========================")

                #Update the window

                window[constants.LATITUDE_TEXT].update("Latitude: "+str(lat))
                window[constants.LONGITUDE_TEXT].update("Latitude: "+str(long))
                window[constants.ALTITUDE_TEXT].update("Altitude: "+str(alt))
                window[constants.SPEED_TEXT].update("Speed: "+str(speed_ms)+" m/s")
                window[constants.TIMESTAMP_TEXT].update("Timestamp: "+str(int(float(h_t)))+":"+str(int(float(m_t)))+":"+str(int(float(s_t))))

                #Upload to sondehub
                if sondehub_enabled and callsign_good:
                    try:
                        uploader.add_telemetry(
                        callsign_dec, # Your payload callsign
                        str(int(float(h_t)))+":"+str(int(float(m_t)))+":"+str(int(float(s_t))), # Time
                        float(lat)+config.LAT_OFFSET, # Latitude
                        float(long)+config.LONG_OFFSET, # Longitude
                        float(alt)+config.ALT_OFFSET, # Altitude
                        frame = int(frame_id),
                        vel_h = str(speed_ms)
                        )
                        print("Uploaded to Sondehub!")
                    except Exception as e:
                        print("Sondehub uploader exception")
                        print(e)
                #Update figures
                gps_count = gps_count + 1
                total_count = total_count + 1
                kb_count = kb_count + len(data)
                updateFigures()
                isSSDV = False
            elif success == packets.GPS_FRAME_INVALID and lat !=0 and long !=0:
                #It is possible that the spacecraft didn't send an altitude
                #Then, we will get an invalid type, but the location is still valid!
                f = open("GPSLog.txt",'a')
                try:
                    f.write(data.decode()+"\n")
                except:
                    pass
                f.close()
                
                print("New GPS frame")
                print("========================")
                print("Frame number "+str(frame_id))
                print("")
                print("Latitude: "+str(lat))
                print("Longitude: "+str(long))
                print("Altitude: Unknown")
                print("GPS string:")
                print(str(lat)+","+str(long))
                print("========================")
                #Update the window

                window[constants.LATITUDE_TEXT].update("Latitude: "+str(lat))
                window[constants.LONGITUDE_TEXT].update("Latitude: "+str(long))
                window[constants.ALTITUDE_TEXT].update("Altitude: UK")

                #Update figures
                gps_count = gps_count + 1
                total_count = total_count + 1
                kb_count = kb_count + len(data)
                updateFigures()
                isSSDV = False
            else:
                if lat == 0 and long == 0:
                    print("[WARN] GPS frame values are zero...")
                    gps_count = gps_count + 1
                    total_count = total_count + 1
                    kb_count = kb_count + len(data)
                    updateFigures()
                else:
                    print("Unable to decode GPS frame!")
                #Update the window

                window[constants.LATITUDE_TEXT].update("Latitude: "+str(lat))
                window[constants.LONGITUDE_TEXT].update("Latitude: "+str(long))
                window[constants.ALTITUDE_TEXT].update("Altitude: "+str(alt))
            
            isSSDV = False
        elif packet_type == packets.OS42_TYPE_TEMP_READING:
            return_code,reading = packets.decode_temp(data)
            isSSDV = False

            if return_code == packets.GPS_FRAME_VALID:
                print("Payload reports a temperature of",reading)
                window[constants.TEMPERATURE_TEXT].update("Temperature: "+str(reading)+" C")
            else:
                print("Unable to decode temperature telemetry frame")
        else:
            print("Unknown packet type")
            print(data.hex())
            uk_count = uk_count + 1
            total_count = total_count + 1
            updateFigures()
            isSSDV = False #Don't skew the time measurement using this

    
        
    if event != constants.TIMEOUT:
        #print(event, values)
        if event == constants.SPACECRAFT_UPDATE:
        	print("Spacecraft set to "+str(values[constants.SPACECRAFT_UPDATE][0]))
        	spacecraft = str(values[constants.SPACECRAFT_UPDATE][0])
        	window[constants.SPACECRAFT_TEXT].update("Spacecraft Name: "+str(spacecraft))
        if event == constants.IMAGE_FLUSH_BUTTON:
            if sg.popup_yes_no('Are you sure you want to delete all imagery?') == 'Yes':
                #Flush imagery here
                os.system("rm -r "+os.getcwd()+"/rx*") #This removes /rx
                os.system("mkdir rx") #Open the directory again

                #Open our check file and write for it to start from the start
                f_imageid = open("imageid.txt",'w')
                f_imageid.write("0")
                f_imageid.close()

                image_count = 0
        if event == constants.COPY_COORDINATES_BUTTON:
            #Copy our coordinates to clipboard
            pyperclip.copy(str(str(lat)+","+str(long)))
                
    if event == sg.WIN_CLOSED:
        break

window.close()
