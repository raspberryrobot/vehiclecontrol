# vehiclecontrol

Control system for RaspberryPi robotic vehicle.

Tested OK with Raspbian Stretch on Raspberry Pi 3 B+.

Motor control interface is Cytron HAT-MDD10.

Written in python3.

4 programs are provided:

	Motor control - rover_control_module_UDP.py
	System commands - rover_system_module_TCP.py
	Video server - rover_video_module_TCP.py
	Startup script - start.py

Step 1 - Create a directory /rover owned by user pi

	$ sudo -s
	$ cd /
	$ mkdir /rover
	$ chown pi:pi /rover

Step 2 - Clone current repo and copy files in directory /rover/bin

	$ cd /rover
	$ git clone https://github.com/raspberryrobot/vehiclecontrol

You should have these files in directory /rover/vehiclecontrol

	rover_control_module_UDP.py
	rover_system_module_TCP.py
	rover_video_module_TCP.py
	start.py

Step 3 - Fix program permissions

	$ cd /rover/vehiclecontrol
	$ chmod +x *.py

Step 4 - Manage startup execution with cron 
	
	$ crontab -e

Add the following line

	@reboot /rover/vehiclecontrol/start.py
	
Step 5 - Reboot

Control programs will be started at next reboot
