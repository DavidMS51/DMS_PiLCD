
#  	lcd_16x2.py
#  	RSS demo application to read BBC UK Newsfeeds
#
#	David Saul david@cd-vision.co.uk
#	22 Nov 2015
#
#	[insprired / based on work  by  Matt Hawkins   http://www.raspberrypi-spy.co.uk/
#	and Ronivaldo Sampaio / Michael Pilcher
#
#	Developement script for Pi_lcd project
#
#	This should work with Python 2 or 3

# Import
import RPi.GPIO as GPIO
import time
from time import sleep
import datetime
from datetime import datetime
from threading import Thread

import feedparser		# needs to be installed first  with "sudo pip install feedparser"
				# or xxxxx for python 3


#setup PiLCD Class access
from DMS_PiLCD1  import DMS_PiLCD

PiLCD=DMS_PiLCD()

#------------------------------------------
#      BBC RSS feed functions


#       get rss text with handling for an IO exception
def getrss(subject):
	#get rss, handle Indexerror - ie if it cannot find the site
        #for anyother error kill the program safely
	msg="X X X X X"
	try:
		msg = feedparser.parse('http://feeds.bbci.co.uk/news/'+subject+'/rss.xml?edition=uk').entries[0].title
	except IndexError:
		msg = "data error"
	except:
		#catch all just in case
		print("general error in getrss")
		quit(0)
	return msg

#       build message from individual rss feeds
def mess_build(subject):
	msg=""
	for i in range(0,len(subject),2):
		msg=msg+"["+subject[i+1]+"] "+getrss(subject[i])+".   "
	return msg



#------------------------------------

# Main

# Initialise display and backlite
PiLCD.lcd_init()
PiLCD.start_PWM()

scbk = True

# Turn on backlight
# Set colour as magenta ish
PiLCD.led_set(100,0,100)


# setup RSS info for BBC website

# Define rss list - format is 'exact rss title','meaningful title'
# Each list entry is in 2 parts firstly the exact RSS search string for the BBC site
# then the title to display
subject=['world','World','uk','UK','politics','Politics','entertainment_and_arts','Ent']

# 'technology','Tech',  # other RSS options on BBC site

# Setup inital message so mess is defined on first pass through 'while' loop
PiLCD.mess = 	mess_build(subject)
rssup = True	# avoid missing first update slot

# Start the scrolling thread
t=Thread(target=PiLCD.lcd_scroll, args=(0.6,2))
t.start()



while True:

	# Get the time and date
	timen = datetime.now().strftime('%a %d %b %H:%M')

	PiLCD.bflag=True		# suspect scrolling while writing other info to display
	sleep(0.2)	

	PiLCD.lcd_string(timen,1,0)

	PiLCD.bflag=False		# restart scrolling
	sleep(0.2)

	# Update RSS feeds approx every 10 minutes
	if datetime.now().strftime('%M')[1] ==  '5' and  rssup == True: 	
		PiLCD.mess =  mess_build(subject)
		print("updating RSS "+timen) 
		rssup = False		# stop repeated RSS fetches

	if datetime.now().strftime('%M')[1] ==  '0':	# reset RSS fetch flag to true
		rssup = True


	sleep(10)

