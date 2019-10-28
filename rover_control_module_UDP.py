#!/usr/bin/python3

# -----------------------------------------------------------------------------
# Libraries
# -----------------------------------------------------------------------------
import RPi.GPIO as GPIO
from time import sleep
import socket
import os

# -----------------------------------------------------------------------------
# Global definitions
# -----------------------------------------------------------------------------
# show debug output
DEBUG = True

# network 
DEFAULT_IP      = '0.0.0.0'
DEFAUL_PORT     = 10001
MAX_BYTES       = 1024
TELEMETRY_IP    = ''
TELEMETRY_PORT  = 10003

# motor stability  
STABILITY_CONTROL = True
decel_delta = -5

# motor control 
L_wheel_delta = 1
R_wheel_delta = 1
motor_speed_max = 100
steering_delta = 0.1

# GPIO definition
GPIO.setmode(GPIO.BCM)  	# GPIO numbering mode
GPIO.setwarnings(False) 	# enable warning from GPIO
AN2 = 12                	# set pwm2 pin on MD10-Hat
AN1 = 13                	# set pwm1 pin on MD10-hat
DIG2 = 26               	# set dir2 pin on MD10-Hat
DIG1 = 24               	# set dir1 pin on MD10-Hat
GPIO.setup(AN2, GPIO.OUT)   # set pin as output
GPIO.setup(AN1, GPIO.OUT)   # set pin as output
GPIO.setup(DIG2, GPIO.OUT)  # set pin as output
GPIO.setup(DIG1, GPIO.OUT)  # set pin as output
p1 = GPIO.PWM(AN1, 100)     # set pwm for M1
p2 = GPIO.PWM(AN2, 100)     # set pwm for M2

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# start_C2
# -----------------------------------------------------------------------------
def start_C2(ip,port):
    global motor_speed_max

    # Open UDP listening control port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ip, port))
    
    # Open UDP telemetry socket
    telemetry_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    telemetry_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    if DEBUG: print('Listening at {}'.format(sock.getsockname()))
        
    motor_L_pwm_mod = 0
    motor_L_pwm_prev = 0
    motor_L_pwm_val = 0 
    motor_L_dir_prev = 0
    motor_L_dir_val = 0
    motor_R_pwm_mod = 0
    motor_R_pwm_prev = 0
    motor_R_pwm_val = 0   
    motor_R_dir_prev = 0
    motor_R_dir_val = 0
    
    while True:
        # Receive data packet
        data, address = sock.recvfrom(MAX_BYTES)
        data_decoded = data.decode()
        data_array = data_decoded.split(',')
        
        # Get remote client IP for telemetry data
        TELEMETRY_IP = address[0]
        
        # Initialize motor telemetry string
        telemetry_data = "$MOT,"
        
        # Get message type
        PS2_msg_type = data_array[0]
        
        # ---------------------------------------------------------------------
        # hat event
        # ---------------------------------------------------------------------
        if PS2_msg_type == '9':
            h=data_array
            
        # ---------------------------------------------------------------------
        # button down event
        # ---------------------------------------------------------------------
        if PS2_msg_type == '10':
            b=data_array
           
        # ---------------------------------------------------------------------
        # button up event
        # ---------------------------------------------------------------------
        if PS2_msg_type == '11': #button up
            b=data_array
            
        # ---------------------------------------------------------------------
        # joystick event
        # ---------------------------------------------------------------------
        if PS2_msg_type == '7': #axis values from left and right joysticks
            lf,lr,rl,rr=int(data_array[1]),int(data_array[2]),int(data_array[3]),int(data_array[4])
            if DEBUG: print("{} {} {} {}".format(lf,lr,rl,rr))
            if(lf > 0):
                motor_L_pwm_val = motor_R_pwm_val = 100
                motor_L_dir_val = motor_R_dir_val = 1
                telemetry_data += "forward"
                if (rl > 0):
                    motor_L_pwm_val = motor_L_pwm_val * steering_delta
                    telemetry_data += " left"
                elif (rr > 0):
                    motor_R_pwm_val = motor_R_pwm_val * steering_delta
                    telemetry_data += " right"
            elif(lr > 0):
                motor_L_pwm_val = motor_R_pwm_val = 100
                motor_L_dir_val = motor_R_dir_val = 0
                telemetry_data += "reverse"
                if (rl > 0):
                    motor_L_pwm_val = motor_L_pwm_val * steering_delta
                    telemetry_data += " left"
                elif (rr > 0):
                    motor_R_pwm_val = motor_R_pwm_val * steering_delta
                    telemetry_data += " right"
            elif(rl > 0) and (lf == 0) and (lr== 0):
                motor_L_pwm_val = motor_R_pwm_val = 100
                motor_L_dir_val = 0
                motor_R_dir_val = 1
                telemetry_data += "pivot left"
            elif(rr > 0) and (lf == 0) and (lr == 0):
                motor_L_pwm_val = motor_R_pwm_val = 100
                motor_L_dir_val = 1
                motor_R_dir_val = 0
                telemetry_data += "pivot right"
            else:
                motor_L_pwm_val = motor_R_pwm_val = 0
                motor_L_dir_val = motor_R_dir_val = 0
                telemetry_data += "stop"
                
        # ---------------------------------------------------------------------
        # stability control - deceleration function
        # ---------------------------------------------------------------------
        if STABILITY_CONTROL:
            if motor_L_dir_prev == motor_R_dir_prev == 1:
                if  motor_L_pwm_val < motor_L_pwm_prev :
                    if motor_R_pwm_val < motor_R_pwm_prev :
                        if DEBUG: print("deceleration")
                        # send telemetry data
                        telemetry_data = "$MOT,deceleration"
                        data = telemetry_data.encode()
                        telemetry_socket.sendto(data, (TELEMETRY_IP, TELEMETRY_PORT))
                        # apply deceleration algorithm
                        for speed in range(motor_speed_max,0,decel_delta):
                            motor_L_pwm_val = speed * L_wheel_delta
                            motor_R_pwm_val = speed * R_wheel_delta
                            if DEBUG: print("[d] {} {}".format(int(motor_L_pwm_val),int(motor_R_pwm_val)))                  
                            if (motor_L_dir_prev == 0) & (motor_R_dir_prev == 0):
                                p1.start(motor_L_pwm_val)
                                GPIO.output(DIG1, GPIO.HIGH)
                                p2.start(motor_R_pwm_val)
                                GPIO.output(DIG2, GPIO.HIGH)
                            elif (motor_L_dir_prev == 1) & (motor_R_dir_prev == 1):
                                p1.start(motor_L_pwm_val)
                                GPIO.output(DIG1, GPIO.LOW)
                                p2.start(motor_R_pwm_val)
                                GPIO.output(DIG2, GPIO.LOW)                          
                            sleep(0.01)
                        motor_L_pwm_val = 0
                        motor_L_pwm_prev = 0
                        motor_R_pwm_val = 0
                        motor_R_pwm_prev = 0
                else:
                    motor_L_pwm_prev = motor_L_pwm_val
                    motor_R_pwm_prev = motor_R_pwm_val
                    
        # ---------------------------------------------------------------------
        # Get reference values 
        # ---------------------------------------------------------------------
        # get reference rover direction 
        motor_L_dir_prev = motor_L_dir_val
        motor_R_dir_prev = motor_R_dir_val
        # get reference maximum motor value 
        if motor_L_pwm_val > motor_R_pwm_val:
            motor_speed_max = motor_L_pwm_val
        else:
            motor_speed_max = motor_R_pwm_val
            
        # ---------------------------------------------------------------------
        # steering delta to correct vehicule alignment
        # ---------------------------------------------------------------------
        motor_L_pwm_val = motor_L_pwm_val * L_wheel_delta
        motor_R_pwm_val = motor_R_pwm_val * R_wheel_delta
 
        # ---------------------------------------------------------------------
        # Apply event values to motor controler input
        # --------------------------------------------------------------------- 
        if motor_L_dir_val == 0:
            p1.start(motor_L_pwm_val)
            GPIO.output(DIG1, GPIO.HIGH)
        if motor_R_dir_val == 0:
            p2.start(motor_R_pwm_val)
            GPIO.output(DIG2, GPIO.HIGH)
        if motor_L_dir_val == 1:
            p1.start(motor_L_pwm_val)
            GPIO.output(DIG1, GPIO.LOW)
        if motor_R_dir_val == 1:
            p2.start(motor_R_pwm_val)
            GPIO.output(DIG2, GPIO.LOW)

        # ---------------------------------------------------------------------
        # Show debug message
        # ---------------------------------------------------------------------
        if DEBUG:
            # show joystick values
            if PS2_msg_type == '7':
               print('{},{},{},{},{}'.format(
                                        int(PS2_msg_type),
                                        int(motor_L_pwm_val),
                                        int(motor_L_dir_val),
                                        int(motor_R_pwm_val),
                                        int(motor_R_dir_val)
                                        ))
            elif PS2_msg_type == '9':
                print('{},{},{}'.format(PS2_msg_type,h[0],h[1]))
            elif PS2_msg_type == '10':
                print('{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
                    PS2_msg_type,b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],b[11],b[12]))
            elif PS2_msg_type == '11':
                print('{},{},{},{},{},{},{},{},{},{},{},{},{},{}'.format(
                    PS2_msg_type,b[0],b[1],b[2],b[3],b[4],b[5],b[6],b[7],b[8],b[9],b[10],b[11],b[12]))

        # ---------------------------------------------------------------------
        # Show/send Telemetry data
        # ---------------------------------------------------------------------
        if DEBUG: print(telemetry_data)
        data = telemetry_data.encode()
        telemetry_socket.sendto(data, (TELEMETRY_IP, TELEMETRY_PORT))

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    if DEBUG: os.system('clear')
    try:
        start_C2(DEFAULT_IP,DEFAUL_PORT)
    except KeyboardInterrupt:
        GPIO.cleanup()
