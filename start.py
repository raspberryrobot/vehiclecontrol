#!/usr/bin/python3
import os

os.system('/rover/bin/rover_system_module_TCP.py &')
os.system('/rover/bin/rover_control_module_UDP.py &')
os.system('/rover/bin/rover_video_module_TCP.py &')
