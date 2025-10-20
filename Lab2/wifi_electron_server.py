import socket
import threading
import json
from smbus import SMBus
import subprocess
import re
from time import sleep, time
from picarx import Picarx
from vilib import Vilib


HOST = "192.168.11.11"
PORT = 65432
power = 10
LEFT, RIGHT, FORWARD, BACKWARD, STOP = 'left', 'right', 'forward', 'backward', 'stop'
curr_dir = STOP
KEY = 'service'
camera_on = False
curr_dir, curr_time, distance = STOP, time(), 0
powerDistMap = { # cm/s
    FORWARD: 0.3,
    BACKWARD: 0.1,
    LEFT: 0.15,
    RIGHT: 0.13,
}

px = Picarx()
power_lock, dir_lock = threading.Lock(), threading.Lock()


def read_speed():
    distance_1 = round(px.ultrasonic.read(), 2)
    sleep(1)
    distance_2 = round(px.ultrasonic.read(), 2)
    diff_dist = distance_2-distance_1
    print(f"speed in cm/s: {diff_dist}")
    return round(diff_dist, 2)

def read_temperature():
    result = subprocess.run(['vcgencmd', 'measure_temp'], capture_output=True, text=True, check=True)
    if result.stderr:
        raise Exception(result.stderr)
    print(f"Temperature stdout: {result.stdout}")
    match = re.search(r'\d+\.\d+', result.stdout)
    if not match:
        raise Exception(f"Temp reading is malformed: {result.stdout}")
    print(f"Temperature: {match.group()}")
    return match.group()

def voltage_to_percent(voltage):
    if voltage >= 8.28:
        return 100
    elif voltage >= 8.0:
        return 90
    elif voltage >= 7.8:
        return 75
    elif voltage >= 7.5:
        return 50
    elif voltage >= 7.0:
        return 25
    elif voltage >= 6.6:
        return 10
    else:
        return 0

def read_battery_level():
    bus = SMBus(1)
    bus.write_word_data(0x14, 0x13, 0)
    msb = bus.read_byte(0x14)
    lsb = bus.read_byte(0x14)
    raw_adc = (msb << 8) | lsb
    
    # convert to battery level
    voltage = raw_adc * 3.3 / 4095 * 3  
    # ADC resolution = 12 bits (0–4095)
    #     https://ptelectronics.ru/wp-content/uploads/AT32F413RCT7.pdf page 20
    # ADC reference voltage: Usually 3.3V
    #     https://ptelectronics.ru/wp-content/uploads/AT32F413RCT7.pdf page 29
    # resistor divider is likely 3:1
    battery_percent = voltage_to_percent(voltage)
    print(f"Raw ADC: {raw_adc}, Voltage: {voltage:.2f} V, Battery: {battery_percent}%")

    return battery_percent

def calculateDistance(curr_time):
    end_time = time()
    if curr_dir is None or curr_dir == STOP:
        curr_time = end_time
        return 0
    dist = powerDistMap[curr_dir]*power*(end_time - curr_time)
    curr_time = end_time
    return dist

def returnDistance(dist):
    return round(dist, 2)

def move(direction, power):
    if direction == STOP:
        px.stop()
    else:
        if direction == FORWARD:
            px.set_dir_servo_angle(0)
            px.set_motor_speed(1, power*0.6)
            px.set_motor_speed(2, -power)
        elif direction == BACKWARD:
            px.set_dir_servo_angle(0)
            px.set_motor_speed(1, -power)
            px.set_motor_speed(2, power*1.6)
        elif direction == LEFT:
            px.set_dir_servo_angle(-30)
            px.set_motor_speed(1, -power)
            px.set_motor_speed(2, -power)
        elif direction == RIGHT:
            px.set_dir_servo_angle(30) 
            px.set_motor_speed(1, power)
            px.set_motor_speed(2, power)

def handle_client_event(service):
    res = {}
    global power
    global power_lock
    global curr_dir
    global camera_on
    global distance
    global curr_time
    try:
        print(f"service: {service}")
        if service.startswith("dir"):
            if '.' in service:
                distance += calculateDistance(curr_time)
                direction = service.split('.')[1]
                print(f"direction: {direction}")
                if direction in ['l', LEFT]:
                    move(LEFT, power)
                    with dir_lock:
                        curr_dir = LEFT
                elif direction in ['r', RIGHT]:
                    move(RIGHT, power)
                    with dir_lock:
                        curr_dir = RIGHT
                elif direction in ['f', FORWARD]:
                    move(FORWARD, power)
                    with dir_lock:
                        curr_dir = FORWARD
                elif direction in ['b', BACKWARD]:
                    move(BACKWARD, power)
                    with dir_lock:
                        curr_dir = BACKWARD
                elif direction in ['s', STOP]:
                    move(STOP, power)
                    with dir_lock:
                        curr_dir = STOP
            print(f"curr_dir: {curr_dir}")
            res['dir'] = curr_dir
            res['speed'] = read_speed()
            res['power'] = power
            res['distance'] = returnDistance(distance)
        elif service in ["battery", "batt"]:
            res['battery'] = read_battery_level()
        elif service in ["temp", "temperature"]:
            res['temperature'] = read_temperature()
        elif service in ["speed"]:
            res['speed'] = read_speed()
            res['power'] = power
        elif service.startswith("power"):
            if '.' in service:
                distance += calculateDistance(curr_time)
                new_power = int(service.split('.')[1])
                print(f"new_power: {new_power}")
                with power_lock:
                    power = new_power
            res['speed'] = read_speed()
            res['power'] = power
            res['distance'] = returnDistance(distance)
            move(curr_dir, power)
            print(f"power updated: {power}")
        elif service in ["dist", "distance"]:
            res['distance'] = returnDistance(distance)
        elif service == "all":
            res['battery'] = read_battery_level()
            res['temperature'] = read_temperature()
            res['speed'] = read_speed()
            res['power'] = power
            res['distance'] = returnDistance(distance)
    except Exception as e:
        print(f"Error occured while reading [{service}]: {str(e)}")

    return res

def handle_client(client):
    with client:
        try:
            data = json.loads(client.recv(1024).decode('utf-8'))
            if not data or KEY not in data:
                return
            print(f"** data: {data[KEY]}")
            res = handle_client_event(data[KEY])

            # test json
            # data = {'battery': 76, 'temp': 45}
            print(res)
            client.sendall(json.dumps(res).encode('utf-8') + b'\n')
        except Exception as e:
            print(f"Error occured while handling client event: {str(e)}")


def main():
    Vilib.camera_start(vflip=False,hflip=False)
    Vilib.display(local=True,web=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        try:
            while True:
                client, addr = s.accept()
                print("server recv from: ", addr)
                thread = threading.Thread(target=handle_client, args=(client,))
                thread.start()
        except KeyboardInterrupt:
            print("Shutting down")
        finally: 
            print("Closing socket")
            s.close()
            Vilib.camera_close()

if __name__ == "__main__":
    main()
