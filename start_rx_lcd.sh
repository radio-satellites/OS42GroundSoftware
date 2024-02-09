pkill -f "rtl_tcp"

echo OS-42 Packet Decoder
echo Written by Sasha VE3SVF
echo ""
echo This will only start the imagery decoder! To decode GPS, run
echo "python3 GPSHandler.py"
echo ""
rtl_tcp & python3 DEMOD.py & python3 send2lcd.py & python3 dashboard.py uselcd

pkill -f "rtl_tcp"
