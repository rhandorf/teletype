import time
import binascii
import urllib # for url unquote
import threading
import pigpio

GPIO_PIN=23
pi = pigpio.pi() 
pi.set_mode(GPIO_PIN, pigpio.INPUT)   
time_wait=(0.022)
in_string=""
howdy=0

binstr_to_ascii = {
  '00011' : 'A' ,
  '11001' : 'B' ,
  '01110' : 'C' ,
  '01001' : 'D' ,
  '00001' : 'E' ,
  '01101' : 'F' ,
  '11010' : 'G' ,
  '10100' : 'H' ,
  '00110' : 'I' ,
  '01011' : 'J' ,
  '01111' : 'K' ,
  '10010' : 'L' ,
  '11100' : 'M' ,
  '01100' : 'N' ,
  '11000' : 'O' ,
  '10110' : 'P' ,
  '10111' : 'Q' ,
  '01010' : 'R' ,
  '00101' : 'S' ,
  '10000' : 'T' ,
  '00111' : 'U' ,
  '11110' : 'V' ,
  '10011' : 'W' ,
  '11101' : 'X' ,
  '10101' : 'Y' ,
  '10001' : 'Z' ,
  #'10111' : '1' ,
  #'10011' : '2' ,
  #'00001' : '3' ,
  #'01011' : '4' ,
  #'10000' : '5' ,
  #'10101' : '6' ,
  #'00111' : '7' ,
  #'00110' : '8' ,
  #'11000' : '9' ,
  #'10110' : '0' ,
  #'00011' : '-' ,
  #'11001' : '?' ,
  #'01110' : ':' ,
  #'01001' : '$' ,
  #'01101' : '!' ,
  #'11010' : '&' ,
  #'10100' : '#' ,
  #'01111' : '(' ,
  #'10010' : ')' ,
  #'11100' : '.' ,
  #'01100' : ',' ,
  #'01010' : '\\' ,
  #'11101' : '/' ,
  #'11101' : '"' ,
  '00100' : ' '
}

def status(gpio, level, tick):
  global in_string
  global howdy
  global binstr_to_ascii
  if (howdy==0):
    in_string=""
    for x in range (0,5):
      time.sleep(time_wait)
      in_string += str(pi.read(GPIO_PIN))
    howdy=1
    print(in_string)
    print(binstr_to_ascii[in_string[::-1]])

cb1 = pi.callback(GPIO_PIN,pigpio.FALLING_EDGE,status)
while True:
  if (cb1.tally() == 0):
    howdy=0
  else:
    string=""
  cb1.reset_tally()
  time.sleep(.1)
