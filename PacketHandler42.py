import os
from subprocess import Popen, PIPE, STDOUT

#OS-42 Packet handler

OS42_TYPE_GPS = 0
OS42_TYPE_IMAGERY = 1
OS42_TYPE_UNKNOWN = -1
OS42_TYPE_SYNC = 5
OS42_TYPE_SUCCESS = 9
OS42_TYPE_GPS_LOCK = 80
OS42_TYPE_TEMP_READING = 90

GPS_FRAME_VALID = 300
GPS_FRAME_INVALID = -300

GPS_MAGIC_WORD = "4750534c434b3131313131"
GPS_SYNC_WORD = "24242"

TEMP_SYNC_WORD = "2121"

def parse_packet(packet):
    #Identify type and send back data
    return 0

def get_packet_type(packet):
    frame = packet.hex()
    #print(frame)

    #0x55 - Imagery
    #0x09 - GPS
    #0x07 - Filler/Sync

    try:
        assert len(frame) > 2
    except:
        return -8

    if frame[0] == '5' and frame[1] == '5':
        #This is imagery!
        return OS42_TYPE_IMAGERY
    
    elif frame == GPS_MAGIC_WORD:
    	#High speed GPS lock
        return OS42_TYPE_GPS_LOCK
    elif frame[0] == TEMP_SYNC_WORD[0] and frame[1] == TEMP_SYNC_WORD[1]:
        return OS42_TYPE_TEMP_READING
    
    if frame[0] == GPS_SYNC_WORD[0] and frame[1] == GPS_SYNC_WORD[1]:
    	#This is a GPS frame
    	return OS42_TYPE_GPS
    	
    #TODO: Implement sync packets
    else:
        return OS42_TYPE_UNKNOWN

def decode_ssdv_packet_info(data):
    #Decodes telemetry info from an SSDV packet
    data = data.split("\n")

    #Grab the callsign field
    callsignfield = data[0]
    
    callsign = callsignfield[10:].replace("\n","")

    if callsign == "kets":
        #This sometimes happens because no packets were decoded
        callsign = "UNKNOWN"
    imageidfield = data[1]

    try:

        imageid = int(imageidfield[9:].replace(" ",""))
    except:
        imageid = -1 #Failure
        
    return callsign,imageid
def decode_ssdv(buffer,callsign_e):
    #Decodes SSDV from a byte buffer and checks if callsigns match

    f = open("rxtemp.ssdv",'wb')
    f.write(buffer)
    f.close()
    
    #os.system("./ssdv -d -l 255 rxtemp.ssdv rxtemp.jpg")

    cmd = './ssdv -d -l 255 rxtemp.ssdv rxtemp.jpg'
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output = p.stdout.read().decode()

    callsign,imageid = decode_ssdv_packet_info(output)

    

    if callsign == callsign_e:
        return OS42_TYPE_SUCCESS,imageid
    else:
        print("SSDV callsign "+str(callsign)+" didn't match the expected callsign ("+str(callsign_e)+")")
        return OS42_TYPE_UNKNOWN,-1
    
def decode_GPS(line):
    #Decode a modified UKHAS OS-42 string
    #$$,UK,79.6691818,-90.5322708,375
    #$$, 165.00,79.6691818,-90.5322708,   0.00,  20.00,  40.00,  39.00,48
    return_type = GPS_FRAME_VALID
    
    try:
        line = line.decode()
        line_parts = line.split(",")

        altitude = line_parts[1].replace(" ","")
        if altitude == "UK" or float(altitude) > 50000: #Alt > 50000 seems to happen with the new prototype???
            return_type = GPS_FRAME_INVALID
        lat = line_parts[2]
        long = line_parts[3]

        frame_id = line_parts[8].replace(" ","")

        #Sanity checks on the data

        lat = float(lat)
        long = float(long)

        speed_ms = line_parts[4].replace(" ","")

        time_h = line_parts[5].replace(" ","")
        time_m = line_parts[6].replace(" ","")
        time_s = line_parts[7].replace(" ","")

        return return_type,altitude,lat,long,frame_id,speed_ms,time_h,time_m,time_s
    except Exception as e:
        print("Exception in GPS packet handler:")
        print(e)
        return GPS_FRAME_INVALID,-4,-4,-4,0

def decode_temp(line):
    return_type = GPS_FRAME_INVALID
    try:
        line = line.decode().split(",")
        reading = int(line[1])
        return GPS_FRAME_VALID,reading
    except Exception as e:
        #print(e)
        return return_type,-800
    
