# vehiclecontrol

Control system for RaspberryPi robotic vehicule.

Tested OK with Raspbian Stretch on Raspberry Pi 3 B+.

Motor control interface is Cytron HAT-MDD10.

Written in python3.

4 programs are provided:

	Motor control - rover_control_module_UDP.py
	System commands - rover_system_module_TCP.py
	Video server - rover_video_module_TCP.py
	Startup script - start.py

Step 1 - Create a directory /rover/bin owned by user pi

	> sudo -s
	> cd /
	> mkdir -p /rover/bin
	> chown -R pi:pi /rover

Step 2 - Clone current repo in /rover/bin/

	> cd /rover/bin
	> git clone https://github.com/framboiserobot/rovercontrol

You should have these files: 

	/rover/bin/rover_control_module_UDP.py
	/rover/bin/rover_system_module_TCP.py
	/rover/bin/rover_video_module_TCP.py
	/rover/bin/start.py

Step 3 - Fix program permissions

	> sudo -s
	> cd /rover/bin
	> chmod +x *.py

Step 4 - Manage startup execution with cron 
	
Startup script: /rover/bin/start.py

	> crontab -e

Add the following line

	@reboot /rover/bin/start.py
