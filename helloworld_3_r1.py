#  	lcd_16x2.py
#  	16x2 LCD basic test script
#
#	David Saul david@cd-vision.co.uk
#	14 November 2015
#
#	[insprired / based on work  by  Matt Hawkins   http://www.raspberrypi-spy.co.uk/]
#
#	display time on topline and a user message on bottom line
#	backlight colours selected by 3 user switches
#
#	this is a standalone application is does NOT need DMS_PiLCD loaded
#
#

# Import
import RPi.GPIO as GPIO
import time
from time import sleep
import datetime
from datetime import datetime

# GPIO to LCD mapping	[BCM GPIO numbers]

LCD_RS = 20	# pin 38
LCD_E  = 19	# pin 35
LCD_D4 = 16	# pin 36
LCD_D5 = 13	# pin 33
LCD_D6 = 12	# pin 32
LCD_D7 = 6	# pin 31

LCD_LEDR = 18	# pin 12
LCD_LEDG = 22	# pin 15
LCD_LEDB = 23   # pin 16

# GPIO to user switch mapping

LCD_SW1 = 27	# pin 13
LCD_SW2 = 25	# pin 22
LCD_SW3 = 5     # pin 29

# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005


# GPIO setup
GPIO.setwarnings(False)      # 		
GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7
GPIO.setup(LCD_LEDR, GPIO.OUT) # Backlight
GPIO.setup(LCD_LEDG, GPIO.OUT) # Backlight
GPIO.setup(LCD_LEDB, GPIO.OUT) # Backlight
GPIO.setup(LCD_SW1, GPIO.IN) # switch 1
GPIO.setup(LCD_SW2, GPIO.IN) # switch 2
GPIO.setup(LCD_SW3, GPIO.IN) # switch 3

# define PWM channels
pr = GPIO.PWM(LCD_LEDR, 60)  # channel= LEDR  frequency=50Hz
pg = GPIO.PWM(LCD_LEDG, 60)  # channel= LEDG  frequency=50Hz
pb = GPIO.PWM(LCD_LEDB, 60)  # channel= LEDB  frequency=50Hz

#---------------------------------------------------------
#define functions

def lcd_init():
	# Initialise display
	lcd_byte(0x33,LCD_CMD) # 110011 Initialise
	lcd_byte(0x32,LCD_CMD) # 110010 Initialise
	lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
	lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
	lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
	lcd_byte(0x01,LCD_CMD) # 000001 Clear display
	time.sleep(E_DELAY)

def lcd_byte(bits, mode):
	# Send byte to data pins
	# bits = data
	# mode = True  for character
	#        False for command

	GPIO.output(LCD_RS, mode) # RS

	# High bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x10==0x10:
		GPIO.output(LCD_D4, True)
	if bits&0x20==0x20:
		GPIO.output(LCD_D5, True)
	if bits&0x40==0x40:
		GPIO.output(LCD_D6, True)
	if bits&0x80==0x80:
		GPIO.output(LCD_D7, True)

  	# Toggle 'Enable' pin
	lcd_toggle_enable()

	# Low bits
	GPIO.output(LCD_D4, False)
	GPIO.output(LCD_D5, False)
	GPIO.output(LCD_D6, False)
	GPIO.output(LCD_D7, False)
	if bits&0x01==0x01:
		GPIO.output(LCD_D4, True)
	if bits&0x02==0x02:
		GPIO.output(LCD_D5, True)
	if bits&0x04==0x04:
		GPIO.output(LCD_D6, True)
	if bits&0x08==0x08:
		GPIO.output(LCD_D7, True)

	# Toggle 'Enable' pin
	lcd_toggle_enable()

def lcd_line_convert(line):
	# contvert line 1-4
	# only 1 and 2 current implimented
	if line == 1:
		line = LCD_LINE_1
	elif line == 2:
		line = LCD_LINE_2
	else:
		line = 0
	return(line)


def lcd_toggle_enable():
	# Toggle enable
	sleep(E_DELAY)
	GPIO.output(LCD_E, True)
	time.sleep(E_PULSE)
	GPIO.output(LCD_E, False)
	sleep(E_DELAY)

def lcd_string(message,line):
	# Send string to display

	line = lcd_line_convert(line)           # convert from line no to line address
	message = message.ljust(LCD_WIDTH," ")

	lcd_byte(line, LCD_CMD)

	for i in range(LCD_WIDTH):
    		lcd_byte(ord(message[i]),LCD_CHR)


def start_PWM():		#start 3 pwm ports

	# start PWM
	pr.start(0)
	pg.start(0)
	pb.start(0)


def led_set(ledr,ledg,ledb):	#change colour brightness
	if ledr > 100 or ledg > 100 or ledb > 100:
		return
	pr.ChangeDutyCycle(ledr)	
	pg.ChangeDutyCycle(ledg)		
	pb.ChangeDutyCycle(ledb)

	return

#------------------------------------

# Main
try:
	# Initialise display and backlite
	lcd_init()
	start_PWM()

	#turn on backlight to white
	led_set(90,90,90)

	# Send some test text

	tline1 = "Raspberry Pi"
	tline2 = "16x2 LCD Test"

	lcd_string(tline1,1)
	lcd_string(tline2,2)

	time.sleep(.5) # .5 second delay

	print()
	print("Basic Pi-LCD test Program")
	print()


	#get user text and update
	tline2 = input("User  text ? ")
	print() 
	if tline2 !="":				#nothing entered leave as initial text
		lcd_string(tline2,2)
		print(" displaying",tline2)
	else:
		print(" leaving as default")
	print()
	print(" Use rear pushes to select backlight colour")
	print()
	print(" Control C to terminate")
	print()


	# set inital backlights basic white
	sr = 95
	sg = 60
	sb = 90


	while True:	# main loop check for switch push and update time
		
		if GPIO.input(LCD_SW1) == False:
			if sr == 0:
				sr = 95
			else: 
				sr = 0
			while GPIO.input(LCD_SW1) == False:
				sleep(.1)
			led_set(sr,sg,sb)

		if GPIO.input(LCD_SW2) == False:
			if sg == 0:
				sg = 60
			else:
				sg = 0
			while GPIO.input(LCD_SW2) == False:
				sleep(.1)
			led_set(sr,sg,sb)

		if GPIO.input(LCD_SW3) == False:
			if sb == 0:
				sb = 90
			else:
				sb = 0
			while GPIO.input(LCD_SW3) == False:
				sleep(0.1)	
			led_set(sr,sg,sb)

		sleep(.1)
		#update time
		cur_time=datetime.now().strftime('%H:%M:%S')
		lcd_string("Pi-LCD  "+cur_time ,1)

finally:
	pr.stop
	pg.stop
	pb.stop
	GPIO.cleanup()

