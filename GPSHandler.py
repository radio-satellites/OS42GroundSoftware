#A simple approach to receiving OS-42 GPS-only telemetry using no GUI
import PacketHandler42 as packets
import socket
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 3006

print("OS-42 GPS packet receiver")
print("Sasha VE3SVF")
print("")

print("Attempting to create and connect socket...")

connected = False

while connected == False:
    try:
        s_tlm = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s_tlm.connect((TCP_IP,TCP_PORT))
        connected = True
    except Exception as e:
        print(e)
        time.sleep(1)
        
print("Success!")

while True:
    frame = s_tlm.recv(1024) #Read a maximum of 1024 bytes
    type_packet = packets.get_packet_type(frame)

    if type_packet == packets.OS42_TYPE_GPS:
        #This is a GPS packet
        success, alt, lat, long, frame_id = packets.decode_GPS(frame)

        if success == packets.GPS_FRAME_VALID:
            f = open("GPSLog.txt",'a')
            f.write(frame.decode()+"\n")
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
        elif success == packets.GPS_FRAME_INVALID and lat !=0 and long !=0:
            #It is possible that the spacecraft didn't send an altitude
            #Then, we will get an invalid type, but the location is still valid!
            f = open("GPSLog.txt",'a')
            f.write(frame.decode()+"\n")
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
        else:
            print("Unable to decode GPS frame!")
            
f.close()
