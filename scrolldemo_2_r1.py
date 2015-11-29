# basic code to test sub-routine class
import time
from time import sleep
import random
import datetime
from datetime import datetime

from threading import Thread

random.seed()		# setup seed based on system time

from DMS_PiLCD1  import DMS_PiLCD

PiLCD=DMS_PiLCD()

# Initialise display and backlite
PiLCD.lcd_init()
PiLCD.start_PWM()

#turn on backlight
PiLCD.led_set_colour('white')
#led_set(40,0,0)

# Send some test text

tline1 = "**Raspberry Pi**"
tline2 = "16x2 LCD Test"

PiLCD.lcd_string(tline1,1,0)

#setup list of colours
col_list = ('red','green','blue','yellow','magenta','orange','pink','violet','cyan','white')

#ini variables
sel_col = random.randint(0,9)	# pick a random start colour
sel_col_tmp = 10		# temp colour variable used to avoid repeats
step_time = .4			# scroll step time, seems to work down to .1 on a Pi 2

PiLCD.mess = tline2

t=Thread(target=PiLCD.lcd_scroll, args=(step_time,2))
t.start()


while True:
	PiLCD.mess=raw_input("New message to display ?")
	PiLCD.bflag=True
	sleep(.2)

	while sel_col == sel_col_tmp:
		sel_col = random.randint(0,9)
	sel_col_tmp = sel_col
	PiLCD.led_set_colour(col_list[sel_col])
	PiLCD.bflag=False

	sleep(0.95)


