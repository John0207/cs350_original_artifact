'''
The MIT License (MIT)

GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
Copyright (C) 2017  Dexter Industries

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

#import libs needed 
import grovepi 
from grove_rgb_lcd import *
from time import sleep
from math import isnan
import json
import subprocess
import decimal

#set ports for light and dht sensors, lcd uses I2c port 
light_sensor = 0 #connect light sensor to port A0 
dht_sensor_port = 7 # connect the DHt sensor to port 7 
dht_sensor_type = 0 # use 0 for the blue-colored sensor and 1 for the white-colored sensor

# set white as backlight color 
# we need to do it just once
# setting the backlight color once reduces the amount of data transfer over the I2C line
setRGB(255,255,255)


# time_to_sleep = .5*60*60    # Take sensor data every 30 minutes 
#For testing :
time_to_sleep = 3

#temp limits :
tooLow = 60.0           # Lower limit in fahrenheit
justRightTemp = 85.0    # Perfect Temp in fahrenheit
tooHigh = 95.0          # Temp Too high
#Humidity Limits
justRightHumid = 80.0   # Perfect humidity

threshold = 57 # light threshold, good value for light/dark room 
# should be adjusted for each room system is in

#Function to determine the background color of the lcd screen 
def calcBG(temp_int, humid_int):    
    bgList = [0,0,0]               #initialize the color array 
    #blue for 85F-95F and <80% 
    if((temp_int > justRightTemp) and (temp_int < tooHigh) and (humid_int < justRightHumid)):
        bgR = 0;                    
        bgB = 255;                  
        bgG = 0;
    #green for between 60F-85F and <80%    
    elif((temp_int >= tooLow) and (temp_int <= justRightTemp) and (humid_int < justRightHumid)):             
        bgR = 0;
        bgB = 0;
        bgG = 255;
    #red for over 95F    
    elif(temp_int >= tooHigh):             
        bgB = 0;
        bgR = 255;                  
        bgG = 0;
    #green and blue for humidity > 80% 
    elif (humid_int >= justRightHumid):
        bgB = 255;
        bgR = 0;
        bgG = 255;
        
    bgList = [bgR,bgG,bgB]          #build list of color values to return
    return bgList;

#Function for converting celcius to fahrenheit 
def CtoF( tempc ):
   tempf = round((tempc * 1.8) + 32, 2);
   return tempf;

#create data file dictionary to store data 
data_file = []

while True:
    try:
        #get light sensor value 
        light_sensor_value = grovepi.analogRead(light_sensor)
        #print results to console 
        print("sensor_value = %d\n" %(light_sensor_value))
        
        # get the temperature and Humidity from the DHT sensor 
        [ temp,hum ] = grovepi.dht(dht_sensor_port,dht_sensor_type)
        
        # use conversion function 
        Fairenheit = CtoF(temp)
        t = str(Fairenheit)
        h = str(hum)
        
        #convert to ints 
        temp_int = int(Fairenheit)
        humid_int = int(hum)
        
        #if light sensor value is under threshold, display message to console
        if light_sensor_value < threshold:
            print("Insufficient Light - No Data Recorded\n")
        
        #if light sensor value is over threshold, write data to json file
        #print values to console and change background color of the lcd accordingly as well
        if light_sensor_value > threshold:            
            data_file.append([temp_int, humid_int])
            with open("data.json", "w") as write_file:
                json.dump(data_file, write_file)                
            #calculate lcd color 
            bgList = calcBG(temp_int, humid_int)
            #change it 
            setRGB(bgList[0],bgList[1],bgList[2])     
            #print data/confirmation to the console             
            print("temp =", t, "F\thumidity =", h,"%")
            print("This data was recorded!\n")

        # check if we have nans
        # if so, then raise a type error exception
        if isnan(temp) is True or isnan(hum) is True:
            raise TypeError('nan error')
        

        # instead of inserting a bunch of whitespace, we can just insert a \n
        # we're ensuring that if we get some strange strings on one line, the 2nd one won't be affected
        # Change C to F in the display 
        setText_norefresh("Temp:" + t + "F\n" + "Humidity :" + h + "%")

    except (IOError, TypeError) as e:
        print(str(e))
        # and since we got a type error
        # then reset the LCD's text
        setText("")

    except KeyboardInterrupt as e:
        print(str(e))
        # since we're exiting the program
        # it's better to leave the LCD with a blank text
        setText("")
        # turn off backlight 
        setRGB(0,0,0)
        break

    # wait before executing loop again 
    sleep(time_to_sleep)

 