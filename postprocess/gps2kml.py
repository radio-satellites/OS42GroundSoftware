import simplekml

#GPS Packet handler from PacketHandler42.py

GPS_FRAME_VALID = 300
GPS_FRAME_INVALID = -300

def decode_GPS(line):
    #Decode a modified UKHAS OS-42 string
    #$$,UK,79.6691818,-90.5322708,375
    #$$, 165.00,79.6691818,-90.5322708,   0.00,  20.00,  40.00,  39.00,48
    return_type = GPS_FRAME_VALID
    
    try:
        line_parts = line.split(",")

        altitude = line_parts[1].replace(" ","")
        if altitude == "UK":
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

f = open("GPSLog.txt",'r')

kml = simplekml.Kml()

for line in f:
    try:
        return_type,altitude,lat,long,frame_id,speed_ms,time_h,time_m,time_s = decode_GPS(line)
        kml.newpoint(name=str(frame_id), coords=[(lat,long,altitude)])
    except Exception as e:
        print("Unable to decode line",e)


kml.save("GPSLog.kml")
