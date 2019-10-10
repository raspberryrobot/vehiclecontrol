#!/usr/bin/python3

# -----------------------------------------------------------------------------
# Libraries
# -----------------------------------------------------------------------------
import socket
import time
import picamera
import sys

# -----------------------------------------------------------------------------
# Global definitions
# -----------------------------------------------------------------------------
DEBUG = True
VIDEO_RESOLUTION = (640,480)
VIDEO_FRAMERATE = 24
VIDEO_FORMAT = 'h264'
VIDEO_LENGTH = -1
SERVER_IP = '0.0.0.0'
SERVER_PORT = 10004

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def start_video_server():
    if DEBUG: print("[MSG]> start video server")
    
    # Open listening TCP socket
    with socket.socket() as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
        server_socket.bind((SERVER_IP, SERVER_PORT))
        server_socket.listen(0)
        if DEBUG: print("[MSG]> listening on %s:%d" % (SERVER_IP, SERVER_PORT))

        # Client is connected
        (client_socket, client_address) = server_socket.accept()
        if DEBUG: print("[MSG]> connection from %s:%d" % (client_address))
        connection = client_socket.makefile('wb')

    # Open camera device
    with picamera.PiCamera() as camera:
        # Set camera configuration
        camera.resolution = VIDEO_RESOLUTION
        camera.framerate = VIDEO_FRAMERATE
        
        # Start camera streaming
        try:
            if DEBUG: print("[MSG]> start video capture")
            camera.start_preview()
            time.sleep(1)
            camera.start_recording(connection, format=VIDEO_FORMAT)
            while True:
                camera.wait_recording(VIDEO_LENGTH)
        finally:
            camera.stop_recording()

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    while 1:
        try:
            start_video_server()
        except KeyboardInterrupt:
            print("\r\n[MSG]> CTRL-C - keyboard interupt")
            sys.exit(0)
        except BaseException as e:
            if DEBUG: print("[MSG]> error: exception %s" % e)
        time.sleep(1)


