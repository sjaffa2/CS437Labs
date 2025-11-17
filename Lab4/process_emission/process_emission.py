import sys
import time
import traceback
from awsiot.greengrasscoreipc.clientv2 import GreengrassCoreIPCClientV2
import argparse
import json
from awsiot.greengrasscoreipc.model import ( PublishToTopicRequest, BinaryMessage, JsonMessage, PublishMessage )

parser = argparse.ArgumentParser(
    description="Greengrass Basic Discovery",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
required = parser.add_argument_group("required arguments")

required.add_argument("--message", required=True,  metavar="", dest="message",
                    help="test message")
required.add_argument("--publish-to-iot-topic", required=True,  metavar="", dest="publish_to_iot_topic",
                    help="IoT topic to the core device publishes to")
required.add_argument("--publish-to-client-topic", required=True,  metavar="", dest="publish_to_client_topic",
                    help="client topic to the core device publishes to")
required.add_argument("--subscribe-to-iot-topic", required=True,  metavar="", dest="subscribe_to_iot_topic",
                      help="IoT topic to the core device subscribes to")
required.add_argument("--subscribe-to-client-topic", required=True,  metavar="", dest="subscribe_to_client_topic",
                      help="client topic to the core device subscribes to")
args = parser.parse_args()

MESSAGE = args.message
PUBLISH_TO_IOT_TOPIC = args.publish_to_iot_topic
PUBLISH_TO_CLIENT_TOPIC = args.publish_to_client_topic
SUBSCRIBE_TO_IOT_TOPIC = args.subscribe_to_iot_topic
SUBSCRIBE_TO_CLIENT_TOPIC = args.subscribe_to_client_topic

MAX_CO2 = {}

def on_receive_emission_data(event):
    try:
        if not hasattr(event, 'binary_message') or not event.binary_message:
            return

        topic = event.binary_message.context.topic
        message = str(event.binary_message.message, 'utf-8')
        print('Topic: %s' % topic)
        print('Received new data from: %s' % message)

        message = json.loads(message)
        thing_name = message['thing_name']
        vehicle_id = message['vehicle_id']

        if 'timestep_time' in message and message['timestep_time'] != -1:
            vehicle_CO2 = message['vehicle_CO2']
            MAX_CO2[thing_name] = vehicle_CO2 if thing_name not in MAX_CO2 or vehicle_CO2 > MAX_CO2[thing_name] else MAX_CO2[thing_name]
            
            print(f'Max CO2 level for thing [{thing_name}] (vehicle_id: [{vehicle_id}]): {MAX_CO2[thing_name]}')
            return
        
        payload = {'thing_name': thing_name, 'vehicle_id': vehicle_id, 'max_CO2': MAX_CO2[thing_name], }
        iot_core_payload = json.dumps(payload)
        client_device_payload = PublishMessage(
            json_message=JsonMessage(
                message=payload
            )
        )
        resp = ipc_client.publish_to_iot_core(
            topic_name=PUBLISH_TO_IOT_TOPIC.replace('+', thing_name),
            qos='0',
            payload=iot_core_payload
        )
        ipc_client.publish_to_topic(
            topic=PUBLISH_TO_CLIENT_TOPIC.replace('+', thing_name),
            publish_message=client_device_payload,
        )
    except:
        traceback.print_exc()


try:
    ipc_client = GreengrassCoreIPCClientV2()

    _, operation = ipc_client.subscribe_to_topic(
        topic=SUBSCRIBE_TO_CLIENT_TOPIC, on_stream_event=on_receive_emission_data)
    print('Successfully subscribed to topic: %s' % SUBSCRIBE_TO_CLIENT_TOPIC)

    try:
        while True:
            time.sleep(10)
    except InterruptedError:
        print('Subscribe interrupted.')

    operation.close()
except Exception:
    print('Exception occurred when using IPC.', file=sys.stderr)
    traceback.print_exc()
    ipc_client.close()
    exit(1)
