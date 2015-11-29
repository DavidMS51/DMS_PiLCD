#  	lcd_16x2.py
#  	16x2 LCD demo application to show of RGB backlight
#
#	David Saul david@cd-vision.co.uk
#	22 Nov 2015
#	
#	http://meanderingpi.wordpress.com	
#
#	[insprired / based on work  by  Matt Hawkins   http://www.raspberrypi-spy.co.uk/]
#

# Import
import RPi.GPIO as GPIO
import time
from time import sleep
import datetime
from datetime import datetime

# Setup access to PiLCD class
from DMS_PiLCD1  import DMS_PiLCD

PiLCD=DMS_PiLCD()

# Local LCD update routine
def uplcd():
	if col == 1:
		colt = "Red"
	elif col == 2:
		colt = "Green"
	elif col == 3:
		colt = "Blue"
 
	PiLCD.lcd_cls(True)
	PiLCD.lcd_string(colt+" Selected",1,0)

	if rl == 100:
		rt = "FP"
	else:
		rt = str(rl)

	if gl == 100:
                gt = "FP"
	else:
		gt = str(gl)

	if bl == 100:
		bt = "FP"
	else:
		bt = str(bl)

	PiLCD.lcd_string("R="+rt+" G="+gt+" B="+bt,2,0)
	


# Initialise display and backlight
PiLCD.lcd_init()
PiLCD.start_PWM()


# Send some wellcome text

tline1 = "RGB Backlight "
tline2 = " PiLCD Demo"

print()
print()
print(tline1,tline2)
print()
print("control C to exit")
print()


PiLCD.lcd_string(tline1,1,0)
PiLCD.lcd_string(tline2,2,0)


col = 0 	#setup initial values
rl = 50
gl = 50
bl = 50

# Turn on backlight to initial values
PiLCD.led_set(rl,gl,bl)

sleep(1)

# display keypress functions on LCD
tline1 = "S1 to sel colour."
tline2 = "S2=up S3=down"

PiLCD.lcd_string(tline1,1,0)
PiLCD.lcd_string(tline2,2,0)


while True:
	# Select colour
	if GPIO.input(PiLCD.LCD_SW1) == False:
		col = col + 1
		if col == 4:
			col = 1
		uplcd()
		while GPIO.input(PiLCD.LCD_SW1) == False:
			sleep(.1)

	# Increase PWM ratio for selected colour
	if GPIO.input(PiLCD.LCD_SW2) == False:
		if col == 1:
			rl = rl + 1
			if rl == 101:
				rl = 100
		elif col == 2:
			gl = gl + 1
			if gl == 101:
				gl = 100
		
		elif col == 3:
			bl = bl + 1
			if bl == 101:
				bl = 100
		PiLCD.led_set(rl,gl,bl)
		uplcd()
	# Decrease PWM ratio for selected colour
	if GPIO.input(PiLCD.LCD_SW3) == False:
		if col == 1:
			rl = rl - 1
			if rl == -1:
				rl = 0
		elif col == 2:
			gl = gl - 1
			if gl == -1:
				gl = 0

		elif col == 3:
			bl = bl - 1
			if bl == -1:
				bl = 0

		PiLCD.led_set(rl,gl,bl)
		uplcd()
	sleep(.1)


