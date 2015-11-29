#  	DMS_PiLCD.py
#	Subroutine Class  for Pi-LCD 16x2 display board
# 
#
#	David Saul david@cd-vision.co.uk
#	www.meanderingpi.wordpress.com
#	1 Nov 2015
#
#	[elements of this code were insprired / based on work 
#	by  Matt Hawkins   http://www.raspberrypi-spy.co.uk/]
#
#	This has been tested with Python 2 and 3 
#	I still tend to work in Python 2 so has seen less testing on 3
#

#import
import RPi.GPIO as GPIO
import time
from time import sleep

import glob		# only required for DS18B20 routines

class DMS_PiLCD:

#----------------------------------------------------------------------------------------
# Standard Pi-LCD hardware lable definitions


#	GPIO to LCD mapping	[BCM GPIO numbers]
	LCD_RS = 20	# pin 38
	LCD_E  = 19	# pin 35
	LCD_D4 = 16	# pin 36
	LCD_D5 = 13	# pin 33
	LCD_D6 = 12	# pin 32
	LCD_D7 = 6	# pin 31

	LCD_LEDR = 18	# pin 12
	LCD_LEDG = 22	# pin 15
	LCD_LEDB = 23   # pin 16

#	GPIO to user switch mapping
	LCD_SW1 = 27	# pin 13
	LCD_SW2 = 25	# pin 22
	LCD_SW3 = 5     # pin 29

# 	Define some device constants
	LCD_WIDTH = 16    # Maximum characters per line
	LCD_CHR = True
	LCD_CMD = False

	LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
	LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
	LCD_LINE_3 = 0x94 # LCD RAM address for the 2nd line - 4x20 line disp only
	LCD_LINE_4 = 0xd4 # LCD RAM address for the 2nd line - 4x20 line disp only


# 	Timing constants
	E_PULSE = 0.0005
	E_DELAY = 0.0005

# 	GPIO setup
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

# 	define PWM channels
	pr = GPIO.PWM(LCD_LEDR, 60)  # channel= LEDR  frequency=50Hz
	pg = GPIO.PWM(LCD_LEDG, 60)  # channel= LEDG  frequency=50Hz
	pb = GPIO.PWM(LCD_LEDB, 60)  # channel= LEDB  frequency=50Hz

#----------------------------------------------------------------------------------------
#	Low level standard functions for Pi-LCD communications.
#	These are used locally by the PiLCD class for
#	LCD serial comms. There should be no reason to call them from programs,
#	used incorrectly they will cause display lockups requiring a power cycle to fix 	


#	Send byte to data pins - using 4 bit nibble mode	
	def lcd_byte(self,bits, mode):
	
	# bits = data
	# mode = True  for character
	#        False for command

	# For an details on 4 bit comms operation see HD44780 datasheets

		GPIO.output(self.LCD_RS, mode) 	# RS

		# High bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(self.LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(self.LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(self.LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(self.LCD_D7, True)

  		# Toggle 'Enable' pin
		self.lcd_toggle_enable()

		# Low bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(self.LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(self.LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(self.LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		self.lcd_toggle_enable()


#	convert line 1-4 to LCD hex RAM address for relevant line start
#	Lines 3 and 4 are only relevant if you 'hacked' a 4 line line display onto the PiLCD board
	def lcd_line_convert(self,line):
		if line == 1:
			line = self.LCD_LINE_1
		elif line == 2:
			line = self.LCD_LINE_2
		elif line == 3:
                       	line = self.LCD_LINE_3
		elif line == 4:
                        line = self.LCD_LINE_4
		else:
			line = 0
		return(line)


#	Toggle enable line on LCD
#	used to latch data into LCD
	def lcd_toggle_enable(self):
		sleep(self.E_DELAY)
		GPIO.output(self.LCD_E, True)
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)
		sleep(self.E_DELAY)

#----------------------------------------------------------------------------------------
#	Main user routines to send charateres to the LCD


#       Initialise display
#       This must be called before anyother commands can
#       can be sent to the LCD
	def lcd_init(self):
		self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
		self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
		self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
		self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
		self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
		self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
		time.sleep(self.E_DELAY)

#	define 1 of the 8 available user characters
	def lcd_defchar(self,char_no,char):
		# char_no = the user defined charater you want to define - 0-7
		# char = bitmap represented as tuple of 8 binary numbers, each representing a 5 pixel row [d7,6,5 are ignored]

		# basic error check on char and char_no to confirm they are  valid
		if char_no > 7 or len(char) != 8:
			return

		char_no = char_no * 8			# convert user char no to memory address
		self.lcd_byte(0x40 + char_no,False)	# setup to send user character data

		self.lcd_byte(char[0],True)		# sent user char
		self.lcd_byte(char[1],True)		# for some reason this does not work as a for loop
		self.lcd_byte(char[2],True)
		self.lcd_byte(char[3],True)
		self.lcd_byte(char[4],True)
		self.lcd_byte(char[5],True)
		self.lcd_byte(char[6],True)
		self.lcd_byte(char[7],True)

		return

#	set cursor to column / row
#	this needs to be sent prior to using lcd_char routine for the first time
	def lcd_setcursor(self,col,row):
		# Far left column = 0
	
		if row < 1 or row > 4 or col < 0 or col > self.LCD_WIDTH:		# basic check for valid coordinates 
			return
		
		row =self.lcd_line_convert(row)	# convert row no. to display hex address
		self.lcd_byte(row+col,self.LCD_CMD)	# move cursor



# 	send charater [in range 0-255] to display at current cursor position
	def lcd_char(self,char):
 		self.lcd_byte(char,self.LCD_CHR)

		# LCD hardware will automatically increment to next position
		# before first use you have to set an initial cursor postion with lcd_curpos(xx) or lcd_setcursor
		#
		# note:- routine will not flow cleanly from line 1 to line 2 because of the way
		#        because of the way the LCD display memory is mapped




#	Send string to display
	def lcd_string(self,message,line,pos):
		# no checking is carried to check 'pos' argument will not overflow display lines
		# for the specfied string length

		line = self.lcd_line_convert(line)      # convert from line no to line address
		line = line + pos			# offset left for start postion
		message = message.ljust(self.LCD_WIDTH," ") # ****** need to check if this is still needed *******

		self.lcd_byte(line, self.LCD_CMD)	# setup text start point

		for i in range(self.LCD_WIDTH):		# send each chartacter to disp
    			self.lcd_byte(ord(message[i]),self.LCD_CHR)




#	Display scrolling text, to allow concurrent scrolling with other display information
#	this needs to be  run with 'threading' rather than as a normal subroutine
#	this will never exit

	# Define global variables to pass data to Thread
	mess = "message"	# this is the message text you want to scroll
	bflag = False		# this suspends scrolling
				# used to avoid clashes when you use other functions
				# to display things on the LCD				
				# set to True to pause scrolling, False to restart
				# note:- you need to add a .02sec sleep after setting
				# bflag to True, to give time for the scroll thread
				# to register the suspend request
	def lcd_scroll(self,speed,line):
		# 'speed' = scroll speed - 0.6 works well, very short times will not be stable
		# 'line' = line to scroll [ must be 1 or 2 ]

		z = 0	# tmp variable
		message = " blank message " 

		if line < 1 or line > 2:	# check for a legal line number
			print ()
			print ("line Error")
			quit()			# stop the thread

		# comment out the above and uncomment these lines when using 'big characters' on
		# 4 line display

# 		if line < 3 or line > 4:        # check for a legal line number
#                       print
#                       print "line Error"
#                       quit()                  # stop the thread

	
		# main scroll routine
		while True:
			if message != self.mess:	#check for and message update being passed to the thread
				message = self.mess			# update scrolled message
				scrollmsg = (self.mess+ "   ")*10	# expand it [ makes the scroll look better ]
				z=0					# re-position to start of scroll
			while self.bflag == True:			# avoid clashes with out functions writing to LCD
				sleep(.01)				# hold here until flag reset
			self.lcd_string(scrollmsg[z:(z+25)],line,0)	# scroll
			time.sleep(speed)
			z=z+1
			if z==len(scrollmsg)-10:			# end of extended message start over
				z=0


#	Clear Display
	def lcd_cls(self,back_lite):

		self.lcd_byte(0x01,self.LCD_CMD)
		if back_lite==False:            # if back_lite = False turn off back lite as well
			self.led_set(0,0,0)
                                       		# else - leave on at current brightness levels

#----------------------------------------------------------------------------------------
# 	PWM control routines

# 	These use the new'ish PWM function in the RPi.GPIO class, this was quite unstable initally but
# 	seems to be much better in the current 1.4.2 Rasbian version


# 	Start 3 PWM Ports 
#	This Routine has to be run before any of the other sub-routines using PWM
#	first if you want to control colour levels with PWM
	def start_PWM(self):

		# start PWM
		self.pr.start(0)
		self.pg.start(0)
		self.pb.start(0)


#	Change Colour intensity levels
	def led_set(self,ledr,ledg,ledb):
		if ledr > 100 or ledg > 100 or ledb > 100:	# if values outside legal range just return
			return
		self.pr.ChangeDutyCycle(ledr)	
		self.pg.ChangeDutyCycle(ledg)		
		self.pb.ChangeDutyCycle(ledb)

		return

#	set display to one a x predefined colours
	def led_set_colour(self,bl_col):
	
		if bl_col == 'red':
			ledr = 90
			ledg = 0
			ledb = 0
		elif bl_col == 'green':
			ledr = 0
			ledg = 90
			ledb = 0
		elif bl_col == 'blue':
			ledr = 0 
			ledg = 0
			ledb = 90
		elif bl_col == 'yellow':
			ledr = 80
			ledg = 60
			ledb = 0
		elif bl_col == 'magenta':
			ledr = 90 
			ledg = 0
			ledb = 90
		elif bl_col == 'orange':
			ledr = 95
			ledg = 20
			ledb = 0
		elif bl_col == 'pink':
			ledr = 95 
			ledg = 0
			ledb = 40
		elif bl_col == 'violet':
			ledr = 60 
			ledg = 0
			ledb = 95
		elif bl_col == 'cyan':
			ledr = 20
			ledg = 95
			ledb = 95
		elif bl_col == 'white':
			ledr = 90
			ledg = 90
			ledb = 95
	
		self.led_set(ledr,ledg,ledb)

		return

#----------------------------------------------------------------------------------------	
# 	Oversize Charater routines


#	Set-up user Characters for oversized numeric display
#	this is called initally to set-up user defined charaters for oversize numeric display
	def lcd_overchar_setup(self):

		#setup Tuples for each bar
		bar1 = (0B11100,0B11110,0B11110,0B11110,0B11110,0B11110,0B11110,0B11100)
		bar2 = (0B00111,0B01111,0B01111,0B01111,0B01111,0B01111,0B01111,0B00111)
		bar3 = (0B11111,0B11111,0B00000,0B00000,0B00000,0B00000,0B11111,0B11111)
		bar4 = (0B11110,0B11100,0B00000,0B00000,0B00000,0B00000,0B11000,0B11100)
		bar5 = (0B01111,0B00111,0B00000,0B00000,0B00000,0B00000,0B00011,0B00111)
		bar6 = (0B00000,0B00000,0B00000,0B00000,0B00000,0B00000,0B11111,0B11111)
		bar7 = (0B00000,0B00000,0B00000,0B00000,0B00000,0B00000,0B00111,0B01111)
		bar8 = (0B11111,0B11111,0B00000,0B00000,0B00000,0B00000,0B00000,0B00000)

		#upload user charaters to LCD
		self.lcd_defchar(0,bar1)
		self.lcd_defchar(1,bar2)
		self.lcd_defchar(2,bar3)
		self.lcd_defchar(3,bar4)
		self.lcd_defchar(4,bar5)
		self.lcd_defchar(5,bar6)
		self.lcd_defchar(6,bar7)
		self.lcd_defchar(7,bar8)



#	display enlarged character starting at specified column pos note each Char take 3 cols
	def lcd_disp_ec(self,col,char):
		# col = left hand edge column for charater
		# char = numberic character to display integer 0-9 
		if char == 0:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(7)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(1)
			self.lcd_char(5)
			self.lcd_char(0)

		elif char ==1:
			self.lcd_setcursor(col,1)
			self.lcd_char(32)
			self.lcd_char(32)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(32)
			self.lcd_char(32)
			self.lcd_char(0)

		elif char ==2:
			self.lcd_setcursor(col,1)
			self.lcd_char(4)
			self.lcd_char(2)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(1)
			self.lcd_char(5)
			self.lcd_char(5)
		
		elif char ==3:
			self.lcd_setcursor(col,1)
			self.lcd_char(4)
			self.lcd_char(2)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(6)
			self.lcd_char(5)
			self.lcd_char(0)

		elif char ==4:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(5)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(32)
			self.lcd_char(32)
			self.lcd_char(0)

		elif char ==5:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(2)
			self.lcd_char(3)
			self.lcd_setcursor(col,2)
			self.lcd_char(6)
			self.lcd_char(5)
			self.lcd_char(0)

		elif char ==6:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(2)
			self.lcd_char(3)
			self.lcd_setcursor(col,2)
			self.lcd_char(1)
			self.lcd_char(5)
			self.lcd_char(0)

		elif char ==7:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(7)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(32)
			self.lcd_char(32)
			self.lcd_char(0)

		elif char ==8:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(2)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(1)
			self.lcd_char(6)
			self.lcd_char(0)

		elif char ==9:
			self.lcd_setcursor(col,1)
			self.lcd_char(1)
			self.lcd_char(2)
			self.lcd_char(0)
			self.lcd_setcursor(col,2)
			self.lcd_char(6)
			self.lcd_char(5)
			self.lcd_char(0)

		return


#----------------------------------------------------------------------------------------
# Extra stuff - not LCD specific

#------------------------------------------
#       DS18B20 functions

#       These fuctions assume you have setp the 1W-GPIO on config

#       Identify folder address for DS18B20
	def sens_add(self):

		base_dir = '/sys/bus/w1/devices/'

		device_folder = glob.glob(base_dir + '28*')[0]
		device_file = device_folder + '/w1_slave'
		return(device_file)

#       Get raw temp data
	def read_temp_file(self,device_file):

		f = open(device_file, 'r')
		lines = f.readlines()
		f.close()
		return lines


#       Return scales temp routine
	def get_temp(self):

	        # get setup 1W locaton
		device_file = self.sens_add()
		raw_data = self.read_temp_file(device_file)

        	# check for valid reading
		ecount = 0	# error counter
		while raw_data[0].find('YES') == -1:
			ecount=ecount+1			# try 10 times  = approx 1 sec
			sleep(0.1)
			raw_data = self.read_temp_file(device_file)
			if ecount == 10:		# return to calling prog after 10 attempts
				temp = "Error"
				return

		ecount = 0	# reset error counter
		t_pos = raw_data[1].find('t=')

		if t_pos != -1:
			temp = raw_data[1][t_pos+2:]            # all good return temp as string

		else:
			temp = "Error"
		return temp

# legacy this is now in RSSdemo
#------------------------------------------
#      BBC RSS feed functions
#
#
#       get rss text with handling for an IO exception
#	def getrss(self,subject):
#                #get rss, handle Indexerror - ie if it cannot find the site
#                #for anyother error kill the program safely
#		msg="X X X X X"
#		try:
#			msg = feedparser.parse('http://feeds.bbci.co.uk/news/'+subject+'/rss.xml?edition=uk').entries[0].title
#		except IndexError:
#			msg = "data error"
#		except:
#                       #catch all just in case
#			print("general error in getrss")
#			quit(0)
#		return msg
#
#       build message from individual rss feeds
#	def mess_build(self,subject):
#		msg=""
#		for i in range(0,len(subject),2):
#			msg=msg+"["+subject[i+1]+"] "+self.getrss(subject[i])+".   "
#		return msg
#

