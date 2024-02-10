pkill -f "python"

echo OS-42 Packet Decoder
echo Written by Sasha VE3SVF
echo ""
echo This will only start the imagery decoder! To decode GPS, run
echo "python3 GPSHandler.py"
echo ""
python3 DEMOD_HACKRF.py & python3 dashboard.py

pkill -f "python"
