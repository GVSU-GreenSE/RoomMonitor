import serial
import csv
import time
from ina219 import INA219

#create INA219 object
ina = INA219(shunt_ohms=0.1,
             max_expected_amps = 0.01,
             address=0x40)
#configure ina
ina.configure(voltage_range=ina.RANGE_16V,
              gain=ina.GAIN_AUTO,
              bus_adc=ina.ADC_128SAMP,
              shunt_adc=ina.ADC_128SAMP)
              
#open serial port - default baudrate 9600
ser = serial.Serial('/dev/ttyUSB0') 
ser.flushInput()    #Clear the queue

#timestamp for file names
timestamp = time.strftime("%Y-%m-%d_%H-%M", time.localtime())

tickcounter = 0

while True:
    try:
      ser_bytes = ser.readline()
      decoded_bytes = ser_bytes[0:len(ser_bytes) - 2].decode("utf-8")
      
      #will only run if line starts with a digit - AKA is a reading  
      if decoded_bytes[0].isdigit():
        #splits read-in line to be processed into CSV
        split_bytes = decoded_bytes.split(' ')
        print (split_bytes)
        
        #open CSV for sensor data and write to it
        with open(timestamp+'_sensor_data.csv','a') as f:
          writer = csv.writer(f, delimiter = ',', quoting = csv.QUOTE_NONE, escapechar = "\n")
          writer.writerow(split_bytes) 
        
        if split_bytes[1] == 'TMP36':
          #take power readings
          v = ina.voltage()
          i = ina.current()
          p = ina.power()
        
          #Formatted versions of voltage, current, power variables
          fv = '{0:0.1f}'.format(v)
          fi = '{0:0.2f}'.format(i)
          fp = '{0:0.4f}'.format(p/1000)
          #put data into a list to be processed for CSV
          power_data = [tickcounter, 'INA219', fv, fi, fp]
          print (power_data)
        
          #open CSV for power consumption data and write to it
          with open(timestamp+'_power_data.csv','a') as f:  
            writer = csv.writer(f, delimiter = ',', quoting = csv.QUOTE_NONE, escapechar = "\n")
            writer.writerow(power_data)
          
          tickcounter += 1
      else:
        #prints any non-reading messages
        print (decoded_bytes)
    except:
      #end program by pressing CTRL + C
      print("Keyboard Interrupt")
      break

ser.close()
