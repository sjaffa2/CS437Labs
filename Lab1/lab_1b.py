#!/bin/env python3

from picarx import Picarx
from enum import Enum
from time import sleep
from tempfile import TemporaryFile
from Mover import Mover
from RoutePlanner import RoutePlanner
from vilib import Vilib

import numpy as np
import math

# Flag for saving environment map into a file 
SAVE_POINTS=True

# States for state machine.
class picar_state(Enum):
    SCAN = 1
    DETECT = 2
    ROUTE = 3
    MOVE = 4
    UPDATE = 5
    CHECK_POSITION = 6
    FINISHED = 7

def init(px):
    '''
    Initialize all servos on PiCar-x
    @param px, A PiCar-X instance.
    '''
    print('[DEBUG] Initializing PiCar-x')
    px.set_dir_servo_angle(0)
    px.set_cam_pan_angle(0)
    px.set_cam_tilt_angle(0)
    sleep(1)

def save_env_map(env_map):
    '''
    Save environmental map into a text file for debugging
    '''
    print(f"[DEBUG] Saving current environment map to file.")
    with open("environment.txt", "w") as outfile:
        np.savetxt(outfile, env_map.astype(int), fmt="%i", delimiter=" ")

def draw_line(env_map,p1,p2):
    '''
    Perform linear interpolation on points in an environment map
    @param env_map, A NumPy binary array, where 1 indicates an object 
                    and 0 indicates empty space.
    @param p1, Starting point for interpolation
    @param p2, Ending point for interpolation
    @remarks Using DDA algorithm as detailed by Professor Tychonievich at https://luthert.web.illinois.edu/blog/posts/492.html  
    '''
    x1 = int(p1[0])
    y1 = int(p1[1])
    x2 = int(p2[0])
    y2 = int(p2[1])

    # Outside the bounds of our environment map.
    if x1 >= 40 or x2 >= 40 or y1 >= 40 or y2 >= 40:
        return

    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))
 
    xinc = dx / steps
    yinc = dy / steps
    x = x1
    y = y1

    for i in range(steps): 
        x = x + xinc
        y = y + yinc
        px_x = round(x)
        px_y = round(y)
        env_map[px_x][px_y] = 1

def add_point_to_map(point,env_map):
    '''
    Adds a value of 1 on the environmental map, which indicates a detected object.
    @param point, An X-Y coordinate 
    @param env_map, A reference to a numpy array which represents objects
                    in the environment.
    '''
    # Starting position from car on environmental map.
    translation_vector = [19, 0]
    
    pt = np.array(point)

    if env_map.shape != (40,40):
        raise ValueError("Variable 'env_map' must be a 40x40 NumPy array")
    elif pt.shape != (2,):
        raise ValueError("Variable 'point' has incorrect number of dimensions")

    new_pt = np.add(translation_vector, pt)
    
    if new_pt[0] >= 40 or new_pt[1] >= 40 or new_pt[0] < 0 or new_pt[1] < 0:
        print(f"[WARN]  Point {new_pt} is outside of environmental map")
        return
    elif new_pt[1] == 0:
        # No object detected.
        return

    env_map[new_pt[0]][new_pt[1]] = 1

def interpolate(points, env_map):
    '''
    Use linear interpolation to find values between points in the environment.
    @param points, A list containing X-Y coordinates
    @param env_map, A NumPy binary array
    @remarks Points with negative values are disgarded
    '''
    count=len(points)-1

    # Interpolate points in between each detected objects.
    for i in range(0,count):
        dx = points[i+1][0]- points[i][0]
        dy = points[i+1][1] - points[i][1]
        x1 = points[i][0]
        y1 = points[i][1]
        x2 = points[i+1][0]
        y2 = points[i+1][1]
        
        # A slope greater than 10 may just be another object in the background.
        if dx > 10:
            continue

        print(f"[DEBUG] Interpolating between points {points[i]} and {points[i+1]}")
        draw_line(env_map, points[i], points[i+1])


def ultrasonic_scan(px, env_map):
    '''
    Perform a scan of the environment using the ultrasonic sensor.
    @param px, An instance of the 'Picarx' class.
    @param env_map, A reference to a numpy array which represents objects
                    in the environment.
    '''
    angles = {
        -60: 0,
        -50: 0,
        -40: 0,
        -30: 0,
        -20: 0,
        -10: 0,
        0: 0,
        10: 0,
        20: 0,
        30: 0,
        40: 0,
        50: 0,
        60: 0
    }

    points = []

    for angle in angles.keys():
        print(f"[DEBUG] Reading distance at {angle} degrees.")
        pt_x = 0
        pt_y = 0
        px.set_cam_pan_angle(angle)
        distance = round(px.ultrasonic.read(), 2)
        # Check for bad sensor readings.
        if distance < 0:
            print(f"[WARN] No object detected or bad sensor reading at {angle} deg.")
            distance = 0
            sleep(.25)
            continue
        else:
            print(f"[DEBUG] Angle={angle} deg, Distance={distance}cm ")
            angles[angle] = distance

        # Handle instances of divide by zero.
        if distance != 0:
            if angle == 0:
                pt_x = 0
                pt_y = round(200 / distance)
            else:
                pt_x = round(200 / (distance * math.sin(math.radians(angle))))
                pt_y = round(200 / (distance * math.cos(math.radians(angle)))) 

        #print(f"[INFO]  New point: ({pt_x},{pt_y})")
        add_point_to_map([pt_x, pt_y], env_map)
        if pt_x > 0 and pt_y > 0:
            points.append((pt_x, pt_y))
        
        sleep(0.25)

    interpolate(points, env_map)

    if SAVE_POINTS == True:
        save_env_map(env_map)

    # Return sensor back to origin.
    px.set_cam_pan_angle(0)
    
def detect_object(px):
    '''
    Check if there is an obstacle in the way with the camera.
    
    @remarks Not implemented yet, just open camera for now.
    '''
    obj_detected = False
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False,web=True)
    Vilib.object_detect_set_model(path="/opt/vilib/detect.tflite")
    Vilib.object_detect_set_labels(path="/opt/vilib/coco_labels.txt")
    Vilib.object_detect_switch(True)
    
def update_car_position(start_point, mv_vector):
    '''
    Update the position of the car on the environment map.
    @param start_point, The car's current position
    @param mv_vector, A resultant vector for the car's velocity
    '''
    print("[INFO]  Updating position of car.")
    start_point[0] += mv_vector[0]
    start_point[1] += mv_vector[1]
    print(f"[INFO]  Car position: {start_point}")

def main():
    '''
    Main routine.
    '''
    px = Picarx()
    init(px)
    state = picar_state.SCAN
    mover = Mover(px)
    router = RoutePlanner()

    # Car starts on the middle row and first column. 
    car_position = [19, 0]

    # Final position is at this point, e.g. 75cm forward and 25cm left.
    end_position = [29, 29]

    # Contains the node list from the shortest path found by A* algorithm.
    dest_path = []

    # Used to adjust position of car.
    mv_vector = []

    # Environment is a 200 cm x 200 cm grid.
    # Composed of 5cm squares, 
    env_grid = np.zeros((40,40), np.int8)

    # State machine for automonous operation.
    while True:
        if state == picar_state.SCAN:
            print(f"[DEBUG] Picar-x state: {state}")
            ultrasonic_scan(px, env_grid)
            state = picar_state.DETECT
            sleep(1)
        elif state == picar_state.DETECT:
            print(f"[DEBUG] Picar-x state: {state}") 
            state = picar_state.ROUTE
            sleep(1)
        elif state == picar_state.ROUTE:
            print(f"[DEBUG] Picar-x state: {state}")
            dest_path = router.a_star_search(env_grid, car_position, end_position)
            if dest_path == []:
                state = picar_state.FINISHED
            else:
                state = picar_state.MOVE
            sleep(1)
        elif state == picar_state.MOVE:
            print(f"[DEBUG] Picar-x state: {state}")
            mv_vector = mover.move_from_path(dest_path)
            state = picar_state.UPDATE
            sleep(1)
        elif state == picar_state.UPDATE:
            print(f"[DEBUG] Picar-x state: {state}")
            update_car_position(car_position, mv_vector)
            # Reset environment map for next scan.
            env_map = np.zeros((40,40), np.int8)
            state = picar_state.SCAN
        elif state ==picar_state.FINISHED:
            print(f"[INFO]  Destination reached !")
            exit(0)
        else:
            state = picar_state.DETECT


if __name__ == "__main__":
    main()
