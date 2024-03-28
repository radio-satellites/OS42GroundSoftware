pkill -f "rtl_tcp"

echo OS-42 Packet Decoder
echo Written by Sasha VE3SVF
echo ""

read -p "Turn on RTL-SDR Bias Tee (y/n)? " answer
case ${answer:0:1} in
    y|Y )
        echo Using RTL-SDR Bias tee
        rtl_biast -d 0 -b 1
        echo Turned on Bias tee...
    ;;
    * )
        echo Not using RTL-SDR Bias tee
    ;;
esac

echo ""
echo Starting RX at 434.0MHz
python3 -m http.server 8080 & rtl_tcp & python3 DEMOD.py & python3 dashboard.py autocall & python3 mapview.py

pkill -f "rtl_tcp"
