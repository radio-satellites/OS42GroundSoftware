f = open("GPSLog.txt",'r')
lat = []
long = []
for line in f:
    line = line.split(",")
    curr_lat = float(line[2])
    curr_lon = float(line[3])
    lat.append(curr_lat)
    long.append(curr_lon)

print(sum(lat)/len(lat))
print(sum(long)/len(long))
