from picarx import Picarx
from time import sleep
import numpy as np

class Mover():

    FORWARD_SPEED = 10
    FORWARD_DURATION = 0.5
    BACKWARD_DURATION = 0.5
    BACKWARD_SPEED = 10

    TURN_DURATION = 0.96
    TURN_SPEED = 10

    def __init__(self, picarx):
        self.px = picarx

    def move_forward(self):
        '''
        Move the car forward approximately 5cm.  
        '''
        print("[DEBUG] Moving forward.")
        # Set direction to origin. 
        self.px.set_dir_servo_angle(0)
        self.px.forward(Mover.FORWARD_SPEED)
        sleep(Mover.FORWARD_DURATION)
        self.px.forward(0)

    def move_backward(self):
        '''
        Move the car backwards.
        '''
        print("[DEBUG] Moving backward.")
        self.px.forward(0)
        sleep(Mover.BACKWARD_DURATION)
        self.px.backward(10)
        sleep(Mover.BACKWARD_DURATION)
        stop()

    def turn_right(self):
        '''
        Turn the car to the right.
        @param px, An instance of a 'Picarx' class.
        '''
        print("[DEBUG] Turning right.")
        self.px.set_dir_servo_angle(45) 
        sleep(Mover.TURN_DURATION)
        self.px.set_motor_speed(1, 80)
        self.px.set_motor_speed(2, 80)
        sleep(Mover.TURN_DURATION)
        self.px.set_dir_servo_angle(0)
        self.px.forward(Mover.FORWARD_SPEED)
        sleep(0.3)
        self.px.forward(0)

    def turn_left(self):
        '''
        Turn the car to the left.
        @param px, An instance of a 'Picarx' class.
        '''
        print("[DEBUG] Turning left.")
        self.px.set_dir_servo_angle(-45)
        sleep(Mover.TURN_DURATION)
        self.px.set_motor_speed(1, -80)
        self.px.set_motor_speed(2, -80)
        sleep(Mover.TURN_DURATION)
        self.move_forward()
        self.px.set_dir_servo_angle(0)
        self.px.forward(Mover.FORWARD_SPEED)
        sleep(0.3)
        self.px.forward(0)

    def stop(self):
        '''
        Stop the car.
        '''
        self.px.forward(0)

    def move_from_path(self,path):
        '''
        Make a series a moves from a given path.
        @param path, A list of tuples where each tuple represents a node in a weighted graph.
        @return A vector which to translate for the final destination node.
        '''
        moves_left = len(path)-1
    
        dest_vector = np.array([0, 0])

        if moves_left >= 2:
            for i in range(0,1):
                cur_move = path[i]
                next_move = path[i+1]
                dx = next_move[0] - cur_move[0]
                dy = next_move[1] - cur_move[1]

                if dx == 1 and dy == 0:
                    self.move_forward()
                    dest_vector[0] += 1
                elif dx == -1 and dy == 0:
                    # Should never occur, but included for completeness.
                    self.move_backward()
                    dest_vector[0] -= 1
                elif dx == 0 and dy == 1:
                    self.turn_left()
                    dest_vector[1] += 1
                elif dx == 0 and dy == -1:
                    self.turn_right()
                    dest_vector[1] -= 1

                # Remove current node, we should've moved by now.
                path.pop(0)
        else:
            for i in range(0, moves_left):
                cur_move = path[i]
                next_move = path[i+1]
                dx = next_move[0] - cur_move[0]
                dy = next_move[1] - cur_move[1]

                if dx == 1 and dy == 0:
                    self.move_forward()
                    dest_vector[0] += 1
                elif dx == -1 and dy == 0:
                    self.move_backward()
                    dest_vector[0] -= 1
                elif dx == 0 and dy == 1 :
                    self.turn_right()
                    dest_vector[1] += 1
                elif dx == 0 and dy == -1:
                    self.turn_left()
                    dest_vector[1] -= 1

                # Remove current node, we should've moved by now.
                path.pop(0)

        return dest_vector

