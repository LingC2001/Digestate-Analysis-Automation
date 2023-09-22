#! /usr/bin/python2

import time
import sys
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library

EMULATE_HX711=False

referenceUnit = 201
offset = 5

if not EMULATE_HX711:
    import RPi.GPIO as GPIO
    from hx711 import HX711
else:
    from emulated_hx711 import HX711

def cleanAndExit():
    print("Cleaning...")

    if not EMULATE_HX711:
        GPIO.cleanup()
        
    print("Bye!")
    sys.exit()
def button_callback(channel):
    offset = val
    print('offset when tare =',round(offset,3))
    print("Tare done! Add weight now...")

    hx.reset()
    hx.tare()
    time.sleep(1)
    
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BCM) # Use physical pin numbering
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.add_event_detect(16,GPIO.RISING,callback=button_callback) # Setup event on pin 10 rising edge

hx = HX711(5, 6)

# I've found out that, for some reason, the order of the bytes is not always the same between versions of python, numpy and the hx711 itself.
# Still need to figure out why does it change.
# If you're experiencing super random values, change these values to MSB or LSB until to get more stable values.
# There is some code below to debug and log the order of the bits and the bytes.
# The first parameter is the order in which the bytes are used to build the "long" value.
# The second paramter is the order of the bits inside each byte.
# According to the HX711 Datasheet, the second parameter is MSB so you shouldn't need to modify it.
hx.set_reading_format("MSB", "MSB")

# HOW TO CALCULATE THE REFFERENCE UNIT
# To set the reference unit to 1. Put 1kg on your sensor or anything you have and know exactly how much it weights.
# In this case, 92 is 1 gram because, with 1 as a reference unit I got numbers near 0 without any weight
# and I got numbers around 184000 when I added 2kg. So, according to the rule of thirds:
# If 2000 grams is 184000 then 1000 grams is 184000 / 2000 = 92.
#hx.set_reference_unit(113)
hx.set_reference_unit(referenceUnit)

hx.reset()



file_object = open('weights.txt', 'w')
file_object.write("")
file_object.close()
# to use both channels, you'll need to tare them both
#hx.tare_A()
#hx.tare_B()
last_weight = 0
count = 0

start_time = time.time()
while True:
    try:
        # These three lines are usefull to debug wether to use MSB or LSB in the reading formats
        # for the first parameter of "hx.set_reading_format("LSB", "MSB")".
        # Comment the two lines "val = hx.get_weight(5)" and "print val" and uncomment these three lines to see what it prints.
        # np_arr8_string = hx.get_np_arr8_string()
        # binary_string = hx.get_binary_string()
        # print binary_string + " " + np_arr8_string
        
        # Prints the weight. Comment if you're debbuging the MSB and LSB issue.
        flask_weight = 679.701+ 118.936
        val = hx.get_weight(5)-flask_weight
        
        #if GPIO.input(16) == 1 and val<2000:
        #   offset = val
        if val > 2000 or val <15:
            val = 0
        # print(current_weight)
        # print (val)
        
        
        # # Open a file with access mode 'a'
        last_values = []
        if abs(last_weight - val) < 1:
            last_values.append(val)
            count += 1
            if count >= 5:
                file_object = open('weights.txt', 'w')
            # # Append 'hello' at the end of file
                avg = sum(last_values)/len(last_values)
                file_object.write(str(round(avg,3)))
                # # Close the file
                file_object.close()
                break
        else:
            count = 0
            last_values = []

        # To get weight from both channels (if you have load cells hooked up 
        # to both channel A and B), do something like this
        #val_A = hx.get_weight_A(5)
        #val_B = hx.get_weight_B(5)
        #print "A: %s  B: %s" % ( val_A, val_B )
        
        last_weight = val
        hx.power_down()
        hx.power_up()
        current_time = time.time()
        if abs(current_time-start_time)>20:
            file_object = open('weights.txt', 'w')
            # # Append 'hello' at the end of file
            file_object.write("Error: Could not determine weight!\n")
            file_object.close()
            break
        time.sleep(0.01)
        
    except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
