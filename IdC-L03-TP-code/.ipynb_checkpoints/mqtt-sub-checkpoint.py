import paho.mqtt.client as mqtt
import time

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
        client.subscribe("idc/iris")
    else:
        print("could not connect, return code:", return_code)


def on_message(client, userdata, message):
    print("Received message: " ,str(message.payload.decode("utf-8")))


broker_hostname ="172.100.10.10"
port = 1883 

client = mqtt.Client("Client2")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect
client.on_message=on_message

client.connect(broker_hostname, port) 
client.loop_start()

try:
    time.sleep(1000000)
finally:
    client.loop_stop()
