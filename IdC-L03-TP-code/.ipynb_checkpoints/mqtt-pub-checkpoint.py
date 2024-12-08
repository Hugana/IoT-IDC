import paho.mqtt.client as mqtt 
import time

broker_hostname = "172.100.10.10"
port = 1883 

def on_connect(client, userdata, flags, return_code):
    if return_code == 0:
        print("connected")
    else:
        print("could not connect, return code:", return_code)

client = mqtt.Client("Client1")
# client.username_pw_set(username="user_name", password="password") # uncomment if you use password auth
client.on_connect=on_connect

client.connect(broker_hostname, port)
client.loop_start()

topic = "idc/iris"
msg_count = 0

msg = []
msg.append('[{"model":"iris-KNN"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
msg.append('[{"model":"iris-GNB"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
msg.append('[{"model":"iris-SVC"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
msg.append('[{"model":"iris-DT"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
msg.append('[{"model":"iris-LR"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')
msg.append('[{"model":"iris-LDA"},{"SepalLengthCm":5.9,"SepalWidthCm":3,"PetalLengthCm":5.1,"PetalWidthCm":1}]')

try:
    while msg_count < len(msg):
        time.sleep(1)
        result = client.publish(topic, msg[msg_count])
        status = result[0]
        if status == 0:
            print("Message "+ str(msg[msg_count]) + " is published to topic " + topic)
        else:
            print("Failed to send message to topic " + topic)
        msg_count += 1
finally:
    client.loop_stop()
