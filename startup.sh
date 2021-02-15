echo "starting redis server"
sudo service redis-server restart

echo "starting mosquitto server"
sudo service mosquitto restart 

echo "starting drive process"
python3 CarDriver.py
