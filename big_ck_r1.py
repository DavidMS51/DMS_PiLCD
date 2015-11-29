#  	lcd_16x2.py
#  	16x2 LCD Development  Script to demo oversize digits
#	if DS18B20 fitted will also display temp is top push pressed
#
#	David Saul david@cd-vision.co.uk
#	20 Sept 2015
#
#	[insprired / based on work  by  Matt Hawkins   http://www.raspberrypi-spy.co.uk/
#	and Ronivaldo Sampaio / Michael Pilcher
#
#	Developement script for Pi_lcd project
#
#

#import
import RPi.GPIO as GPIO
import time
from time import sleep
import random
import datetime
from datetime import datetime

from DMS_PiLCD1  import DMS_PiLCD

PiLCD=DMS_PiLCD()



random.seed()		# setup seed based on system time

#display / update AM-PM indicator
def ampm(morn_eve):
	if morn_eve == "PM":
        	PiLCD.lcd_setcursor(14,2)
	        PiLCD.lcd_char(ord('P'))
        	PiLCD.lcd_char(ord('M'))
	else:
        	PiLCD.lcd_setcursor(14,2)
	        PiLCD.lcd_char(ord('A'))
        	PiLCD.lcd_char(ord('M'))

# check monentary pushes
# if yes and DS18B20 connected display temp
def temp_push_check():
	if GPIO.input(PiLCD.LCD_SW1) == False:
		PiLCD.lcd_cls(True)
		try:
			temp=PiLCD.get_temp()
	
	                #display dec point
			PiLCD.lcd_setcursor(7,1)
			PiLCD.lcd_char(5)

	                #display temp  (in range 0 to 99 deg C)
			PiLCD.lcd_disp_ec(1,int(temp[0]))
			PiLCD.lcd_disp_ec(4,int(temp[1]))
			PiLCD.lcd_disp_ec(8,int(temp[2]))

        	        #display 'deg C'
			PiLCD.lcd_setcursor(11,1)
			PiLCD.lcd_char(ord("o"))
			PiLCD.lcd_char(1)
			PiLCD.lcd_char(7)
			PiLCD.lcd_setcursor(12,2)
			PiLCD.lcd_char(1)
			PiLCD.lcd_char(5)	
	
		except:
			PiLCD.lcd_string( "Cannot find",1,0)
			PiLCD.lcd_string( "DS18B20 Sensor ?",2,0)


		sleep(2)

		#clear display and force refresh of am /pm 
		PiLCD.lcd_cls(True)
		if int(datetime.now().strftime('%H')) >=  12:
		        ampm("PM")
		else:
		        ampm("AM")

	return


#------------------------------------

# Main

# Initialise display and backlite
PiLCD.lcd_init()
PiLCD.start_PWM()

#turn on backlight
PiLCD.led_set_colour('white')

# Setup user Characters for display
PiLCD.lcd_overchar_setup()

#Make sure display is inialised to recieve charater data
PiLCD.lcd_setcursor(1,1)

count = 0	# temp count variable

# initial set of  the AM / PM indicator
if int(datetime.now().strftime('%H')) >=  12:
	ampm("PM")
else:
	ampm("AM")

while True:

# get the time
# coment out either 12 or 24 format as required
#       timen = datetime.now().strftime('%H%M%S')        #24 hour format
	timen = datetime.now().strftime('%l%M%S')        #12 hour format
	
# update the AM / PM indicator
	if datetime.now().strftime('%H%M') == "1200":
		ampm("PM")		
	elif datetime.now().strftime('%H%M') == "0000":
		ampm("AM")

# logic for flashing central colon

	if int(timen[5:6]) % 2 ==1:
		PiLCD.lcd_setcursor(7,1)
		PiLCD.lcd_char(165)
		PiLCD.lcd_setcursor(7,2)
		PiLCD.lcd_char(165)
	else:
		PiLCD.lcd_setcursor(7,1)
		PiLCD.lcd_char(32)
		PiLCD.lcd_setcursor(7,2)
		PiLCD.lcd_char(32)
	
# display the time as big characters

	if timen[0] == '1' or timen[0] == '2':		#pad with leading zero if needed
		PiLCD.lcd_disp_ec(1,int(timen[0]))
	else:
		PiLCD.lcd_disp_ec(1,0)
	
	PiLCD.lcd_disp_ec(4,int(timen[1]))
	PiLCD.lcd_disp_ec(8,int(timen[2]))
	PiLCD.lcd_disp_ec(11,int(timen[3]))
	
	# simple delay loop with scan for top push
	# if push detected display temp for 2 seconds
	while count < 6:
		sleep(.1)
		temp_push_check()		
		count = count +1

	count = 0 
