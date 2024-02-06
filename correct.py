from PIL import Image
import sys

args = list(sys.argv)

im = Image.open(args[1])
im_out = Image.new('RGB',(640,480))
f = open("OS42CORR_640x480.txt",'r')

correction = []

w,h = 640,480

f_lines = f.read().split("\n")

px = im.load()

#Parse correction file

for line in f_lines:
    line = line[0:len(line)-1]
    pixels = line.split(".")
    correction.append(pixels)

#Find largest value

for y in range(h):
    for x in range(w):
        corrlist = correction[y][x].replace("(","").replace(")","").split(",")
        im_out.putpixel((x,y),(round((px[x,y][0]+round(int(corrlist[0])/2))/2),round((px[x,y][1]+round(int(corrlist[1])/2))/2),round((px[x,y][2]+round(int(corrlist[2])/2))/2)))

f.close()

im_out.save(args[2])
