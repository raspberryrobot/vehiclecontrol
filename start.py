#!/usr/bin/python3
import os

os.system('/rover/vehiclecontrol/rover_system_module_TCP.py &')
os.system('/rover/vehiclecontrol/rover_control_module_UDP.py &')
os.system('/rover/vehiclecontrol/rover_video_module_TCP.py &')
