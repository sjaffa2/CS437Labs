# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0.

from awsiot.greengrass_discovery import DiscoveryClient
from awsiot import mqtt_connection_builder
from awscrt import io, http
from awscrt.mqtt import QoS
import time, json
import os
import pandas as pd

allowed_actions = ['both', 'publish', 'subscribe']

# --------------------------------- ARGUMENT PARSING -----------------------------------------
import argparse, uuid

parser = argparse.ArgumentParser(
    description="Greengrass Basic Discovery",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
required = parser.add_argument_group("required arguments")
optional = parser.add_argument_group("optional arguments")

# Required Arguments
# required.add_argument("--cert", required=True,  metavar="", dest="input_cert",
#                     help="Path to the certificate file to use during mTLS connection establishment")
# required.add_argument("--key", required=True,  metavar="", dest="input_key",
#                     help="Path to the private key file to use during mTLS connection establishment")
required.add_argument("--region", required=True,  metavar="", dest="input_signing_region",
                      help="The region to connect through.")
# required.add_argument("--thing_name", required=True,  metavar="", dest="input_thing_name",
#                       help="The name assigned to your IoT Thing.")

# Optional Arguments
# optional.add_argument("--ca_file",  metavar="", dest="input_ca",
#                       help="Path to optional CA bundle (PEM)")
optional.add_argument("--topic", default="emission",  metavar="", dest="input_topic",
                      help="Topic")
optional.add_argument("--message", default="Hello World!",  metavar="", dest="input_message",
                      help="Message payload")
optional.add_argument("--max_pub_ops", type=int, default=10,  metavar="", dest="input_max_pub_ops", 
                    help="The maximum number of publish operations (optional, default='10').")
optional.add_argument("--print_discover_resp_only", type=bool, default=False,  metavar="", dest="input_print_discovery_resp_only",
                    help="(optional, default='False').")
optional.add_argument("--mode", default='both',  metavar="", dest="input_mode",
                    help=f"The operation mode (optional, default='both').\nModes:{allowed_actions}")
optional.add_argument("--proxy_host",  metavar="", dest="input_proxy_host",
                      help="HTTP proxy host")
optional.add_argument("--proxy_port", type=int, default=0,  metavar="", dest="input_proxy_port",
                      help="HTTP proxy port")
optional.add_argument("--client_id",  metavar="", dest="input_clientId", default=f"mqtt5-sample-{uuid.uuid4().hex[:8]}",
                    help="Client ID")

# args contains all the parsed commandline arguments used by the sample
args = parser.parse_args()
# --------------------------------- ARGUMENT PARSING END -----------------------------------------



def on_connection_interupted(connection, error, **kwargs):
    print('connection interrupted with error {}'.format(error))


def on_connection_resumed(connection, return_code, session_present, **kwargs):
    print('connection resumed with return code {}, session present {}'.format(return_code, session_present))


# Try IoT endpoints until we find one that works
def try_iot_endpoints(thing_name, thing_cert, thing_key, region):
    tls_options = io.TlsContextOptions.create_client_with_mtls_from_path(thing_cert, thing_key)
    # if (args.input_ca is not None):
    #     tls_options.override_default_trust_store_from_path(None, args.input_ca)
    tls_context = io.ClientTlsContext(tls_options)

    socket_options = io.SocketOptions()

    proxy_options = None
    # if args.input_proxy_host is not None and args.input_proxy_port != 0:
    #     proxy_options = http.HttpProxyOptions(args.input_proxy_host, args.input_proxy_port)

    print(f"Connecting {thing_name}...")
    print('    Performing greengrass discovery...')
    discovery_client = DiscoveryClient(
        io.ClientBootstrap.get_or_create_static_default(),
        socket_options,
        tls_context,
        region, None, proxy_options)
    resp_future = discovery_client.discover(thing_name)
    discover_response = resp_future.result()

    print("    Received a greengrass discovery result! Not showing result for possible data sensitivity.")

    # if (args.input_print_discovery_resp_only):
    #     print("Error with greengrass discovery for [{}]".format(thing_name))
    #     continue

    for gg_group in discover_response.gg_groups:
        for gg_core in gg_group.cores:
            for connectivity_info in gg_core.connectivity:
                try:
                    print(
                        f"    Trying core {gg_core.thing_arn} at host {connectivity_info.host_address} port {connectivity_info.port}")
                    mqtt_connection = mqtt_connection_builder.mtls_from_path(
                        endpoint=connectivity_info.host_address,
                        port=connectivity_info.port,
                        cert_filepath=thing_cert,
                        pri_key_filepath=thing_key,
                        ca_bytes=gg_group.certificate_authorities[0].encode('utf-8'),
                        on_connection_interrupted=on_connection_interupted,
                        on_connection_resumed=on_connection_resumed,
                        client_id=thing_name,
                        clean_session=False,
                        keep_alive_secs=30)

                    connect_future = mqtt_connection.connect()
                    connect_future.result()
                    print('    √ Connected!')
                    return mqtt_connection

                except Exception as e:
                    print('X Connection failed with exception {}'.format(e))
                    continue

    exit('X All connection attempts failed')


certs_folder = "../../step_1/certs"
certificate_formatter = os.path.join(certs_folder, "{}-certificate.pem.crt")
key_formatter = os.path.join(certs_folder, "{}-private.pem.key")
topic_formatter = "client/{}/{}"
topic_processed_in_core_formatter = topic_formatter + "/local_processed"
topic_send_to_cloud_formatter = topic_formatter + "/cloud"
data_formatter = "../../data/databk/vehicle{}.csv"
thing_names = [
    # "twooxDrrhTQnEZ1FGD", 
    # "twonXO4FwP6f93D07f", 
    # "twom36kfODVIvn41Vm",
    "onevJgIC8J74abVtXD",
    # "one85rng3PAhbf9YCZ"
]
thing_cert_ids = [
    # "d49ffa377b018169e220da6cb79ce0aeaa85a9f228daa68a42169988467b6048", 
    # "7498fca262d6320058c9324e33548b9ca9c455910e632497ed65e164f986ddd7", 
    # "47f1450237afe1a3ed152f4d619e4c4106f8a76cfd8ac7f491b07500b45c477a",
    "ea06197d2ba4264480b6b3aed8cde60ccbd9be2a478b17875ed7a505e4a8dcb1",
    # "27aefb0135c06dfa6722420d93c006c0781796eaf2091b9a19454a6fe95f417f"
]
device_start, device_end = 1, 4
connections = []
for thing_name, thing_cert_id in zip(thing_names, thing_cert_ids):
    mqtt_connection = try_iot_endpoints(
        thing_name = thing_name,
        thing_cert = certificate_formatter.format(thing_cert_id),
        thing_key  = key_formatter.format(thing_cert_id),
        region     = args.input_signing_region
    )
    connections.append(mqtt_connection)
 

if args.input_mode == 'both' or args.input_mode == 'subscribe':
    def on_publish(topic, payload, dup, qos, retain, **kwargs):
        print('Publish received on topic {}: {}'.format(topic, payload))
    print("Listening to topic...")
    for thing_name, mqtt_connection in zip(thing_names, connections):
        print(f"    - {topic_processed_in_core_formatter.format(thing_name, args.input_topic)}")
        subscribe_future, _ = mqtt_connection.subscribe(
            topic_processed_in_core_formatter.format(thing_name, args.input_topic), 
            QoS.AT_MOST_ONCE, 
            on_publish
        )
        subscribe_result = subscribe_future.result()

print("done")

if args.input_mode == 'both' or args.input_mode == 'publish':
    while True:
        print("send now?")
        x = input()
        if x != "s":
            time.sleep(1)
            continue
        for idx, (thing_name, mqtt_connection) in enumerate(zip(thing_names, connections)):
            df = pd.read_csv(data_formatter.format(idx+3))
            message = {}
            message['thing_name'] = thing_name

            # construct data
            data = []
            topic = topic_formatter.format(thing_name, args.input_topic)
            topic_cloud = topic_send_to_cloud_formatter.format(thing_name, args.input_topic)
            print(f"Publishing to {topic_cloud}")
            print(f"Publishing to {topic}")
            for index, row in df.iterrows():
                row_dict = row.to_dict()
                # data.append(row_dict)
                row_dict['thing_name'] = thing_name
                payload = json.dumps(row_dict)
                pub_future, _ = mqtt_connection.publish(
                    topic_cloud, 
                    payload, 
                    QoS.AT_LEAST_ONCE
                )
                publish_completion_data = pub_future.result()
                # message['data'] = data

                # publish
                topic = topic_formatter.format(thing_name, args.input_topic)
                # payload = json.dumps(message)
                pub_future, _ = mqtt_connection.publish(
                    topic, 
                    payload, 
                    QoS.AT_LEAST_ONCE
                )
                # self.client.publishAsync(topic, payload, 0, ackCallback=self.customPubackCallback)
                publish_completion_data = pub_future.result()
            pub_future, _ = mqtt_connection.publish(
                topic, 
                json.dumps({'thing_name': thing_name, 'vehicle_id': f"veh{idx}", 'timestep_time': -1}), 
                QoS.AT_LEAST_ONCE
            )
            # self.client.publishAsync(topic, payload, 0, ackCallback=self.customPubackCallback)
            publish_completion_data = pub_future.result()
            print('Successfully published to topic {} with payload\n'.format(topic))
        time.sleep(1)