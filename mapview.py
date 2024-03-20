import tkinter
import tkintermapview
import sondehub
from PIL import Image, ImageTk
import os
import sys

# create tkinter window
root_tk = tkinter.Tk()
root_tk.geometry(f"{1000}x{700}")
root_tk.title("OS-42 Map View")

callsign = "OS42-2"

# create map widget
map_widget = tkintermapview.TkinterMapView(root_tk, width=1000, height=700, corner_radius=0)
map_widget.pack(fill="both", expand=True)

# set other tile server (standard is OpenStreetMap)
if "googleearth" in list(sys.argv):
    map_widget.set_tile_server("https://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}&s=Ga", max_zoom=22)  # google satellite

# set current position with address
map_widget.set_position(43.693236, -79.483654, marker=False)
map_widget.set_zoom(10)

#Set up the path of the balloon
path_1 = map_widget.set_path([(0,0),(0,0),(0,0),(0,0)])

#Create balloon icon
current_path = os.path.join(os.path.dirname(os.path.abspath(__file__)))
balloon_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "balloon.png")).resize((40,70)))
parachute_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "parachute_cyan.png")).resize((40,70)))
#burst_image = ImageTk.PhotoImage(Image.open(os.path.join(current_path, "pop-marker.png")).resize((16,16)))

#Create balloon marker
balloon_marker = map_widget.set_marker(0.0, 0.0, text=callsign+" Alt: N/A", icon=balloon_image)


initial = True

path = []

counter = 0

ascending = True
wasascending = True
#setPopNow = False

last_altitude = 0

ascent_alts = [0] #Used for calculating ascent rate

ascent_rate = 0

"""
def calculate_ascent():
    global ascent_alts
    if len(ascent_alts) >= 4:
        #Update ascent rate
        ascent_rate = round(sum(ascent_alts)/len(ascent_alts),ndigits=2)
        ascent_alts = []
        return ascent_rate
    else:
        return ascent_rate
"""
def on_message(message):
    try:
        global path_1
        global balloon_marker
        global initial
        global counter
        global last_altitude
        global ascending
        global wasascending
        #global setPopNow
        if initial:
            #Weird compatability issues
            for i in range(4):
                path_1.add_position(message['lat'],message['lon'])
                path_1.remove_position(0,0)

            initial = False
        #print("[DEBUG] Adding "+str(message['lat'])+","+str(message['lon']))
        print("[DEBUG] ascending="+str(ascending)+", last_altitude="+str(last_altitude)+",alt="+str(message['alt'])+", wasascending="+str(wasascending))
        if message['alt'] >= last_altitude-3 and wasascending:
            ascending = True
        else:
            ascending = False
            wasascending = False
            setPopNow = True
        last_altitude = message['alt']
        if len(path) >=4:
            path.append([message['lat'],message['lon']])
            balloon_marker.delete()
            if ascending:
                balloon_marker = map_widget.set_marker(message['lat'],message['lon'],text=callsign+" Alt: "+str(int(message['alt']))+"m", icon=balloon_image)
            else:
                balloon_marker = map_widget.set_marker(message['lat'],message['lon'],text=callsign+" Alt: "+str(int(message['alt']))+"m (descending)", icon=parachute_image)
            if counter % 20 == 0:
                map_widget.set_position(message['lat'],message['lon'], marker=False)
            #if setPopNow:
            #    setPopNow = False
            #    burst_marker = map_widget.set_marker(message['lat'],message['lon'],text=callsign+" Alt: "+str(int(message['alt']))+"m (burst)", icon=burst_image)
        else:
            for i in range(4):
                path.append([message['lat'],message['lon']])
            map_widget.set_position(message['lat'],message['lon'], marker=False)
        path_1.delete()
        path_1 = map_widget.set_path(path)
        counter = counter + 1
        #print(len(path)) #For debugging memory issues
    except Exception as e:
        print(e)

stream = sondehub.Stream(on_message=on_message, prefix="amateur",sondes=[callsign])

root_tk.mainloop()
