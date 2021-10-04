import time
import binascii
import urllib # for url unquote
import threading
import pigpio
import tweepy
import json
import requests
import logging
import time
import credentials

pi = pigpio.pi() # connect to local Pi

consumer_key = credentials.API_key
consumer_secret_key = credentials.API_secret_key
access_token = credentials.access_token
access_token_secret = credentials.access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_secret_key)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

try:
    api.verify_credentials()
    print("Authentication Successful")
except:
    print("Authentication Error")

pi.set_mode(2, pigpio.OUTPUT)

gpio8period      = 20 # period of 1 bit to achieve 45bps was 20

ColumnCurrentPosition = 1
ColumnMax             = 68

# first we map ascii to the possible ascii chars
ascii_to_baudot_char = {
  'a':'A',
  'b':'B',
  'c':'C',
  'd':'D',
  'e':'E',
  'f':'F',
  'g':'G',
  'h':'H',
  'i':'I',
  'j':'J',
  'k':'K',
  'l':'L',
  'm':'M',
  'n':'N',
  'o':'O',
  'p':'P',
  'q':'Q',
  'r':'R',
  's':'S',
  't':'T',
  'u':'U',
  'v':'V',
  'w':'W',
  'x':'X',
  'y':'Y',
  'z':'Z',
  'A':'A',
  'B':'B',
  'C':'C',
  'D':'D',
  'E':'E',
  'F':'F',
  'G':'G',
  'H':'H',
  'I':'I',
  'J':'J',
  'K':'K',
  'L':'L',
  'M':'M',
  'N':'N',
  'O':'O',
  'P':'P',
  'Q':'Q',
  'R':'R',
  'S':'S',
  'T':'T',
  'U':'U',
  'V':'V',
  'W':'W',
  'X':'X',
  'Y':'Y',
  'Z':'Z',
  '1':'1',
  '2':'2',
  '3':'3',
  '4':'4',
  '5':'5',
  '6':'6',
  '7':'7',
  '8':'8',
  '9':'9',
  '0':'0',
  '-': '-',
  '?': '?',
  ':': ':',
  '$': '$',
  '!': '!',
  '&': '&',
  '#': '#',
  '(': '(',
  ')': '(',
  '.': '.',
  ',': ',',
  '\'': '\'',
  '/': '/',
  '"': '"',
  ' ': ' ' 
}

# then we map limted set to baudot
# see http://rabbit.eng.miami.edu/info/baudot.html
ascii_to_binstr = {
  'A'  : '00011',
  'B'  : '11001',
  'C'  : '01110',
  'D'  : '01001',
  'E'  : '00001',
  'F'  : '01101',
  'G'  : '11010',
  'H'  : '10100',
  'I'  : '00110',
  'J'  : '01011',
  'K'  : '01111',
  'L'  : '10010',
  'M'  : '11100',
  'N'  : '01100',
  'O'  : '11000',
  'P'  : '10110',
  'Q'  : '10111',
  'R'  : '01010',
  'S'  : '00101',
  'T'  : '10000',
  'U'  : '00111',
  'V'  : '11110',
  'W'  : '10011',
  'X'  : '11101',
  'Y'  : '10101',
  'Z'  : '10001',
  '1'  : '10111',
  '2'  : '10011',
  '3'  : '00001',
  '4'  : '01011',
  '5'  : '10000',
  '6'  : '10101',
  '7'  : '00111',
  '8'  : '00110',
  '9'  : '11000',
  '0'  : '10110',
  '-'  : '00011',
  '?'  : '11001',
  ':'  : '01110',
  '$'  : '01001',
  '!'  : '01101',
  '&'  : '11010',
  '#'  : '10100',
  '('  : '01111',
  ')'  : '10010',
  '.'  : '11100',
  ','  : '01100',
  '\'' : '01010',
  '/'  : '11101',
  '"'  : '11101',
  ' '  : '00100'
}

needs_shift_up = (
  '1',
  '2',
  '3',
  '4',
  '5',
  '6',
  '7',
  '8',
  '9',
  '0',
  '-',
  '?',
  ':',
  '$',
  '!',
  '&',
  '#',
  '(',
  ')',
  '.',
  ',',
  '\'',
  '/',
  '"'
)

#def init(gpio_arg):
def init():
  """
  initialize teletype i/o
  """
  txbaudot("01000") # cr
  time.sleep(1.0)
  txbaudot("00010") # lf


def finish():
  txbaudot("11111")
  init()

# establish timer for TTY Motor

def motor_start(time_secs=0):
  """
  turn on motor
  """
  global MotorTimerCtr, MotorTimerVal

  if (not MotorTimerCtr) :
    #print "Motor start"
    gpio.output(PWR_RLY,gpio.LOW)
    time.sleep(.25)
  
  if not time_secs:
    MotorTimerCtr = MotorTimerVal
  else:
    #print "motor_start(): non-standard timeout value: %d" % time_secs
    MotorTimerCtr = time_secs

def motor_stop():
  """
  turn off motor, turn off data relay
  """
  global MotorTimerCtr
  gpio.output(PWR_RLY,gpio.HIGH)
  time.sleep(2.0)
  gpio.output(DATA_RLY,gpio.HIGH)
  MotorTimerCtr = 0

def test(s):
  """
  various tests
  """
  if (s == 'allpats'):
    """
    test mapping tables by attempt to print out all possible codes
    """
    #print 'allpats'
    for i in range(0,256):
      if (ascii_to_baudot_char.has_key(chr(i))): # if first reduce mapping table has key
        a = ascii_to_baudot_char[chr(i)]
        #print 'ascii_to_baudot_char(%d): %s' % (i,a)
        if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
          b = ascii_to_binstr[a]
          if (b != '00000'):
            #print 'test(%s)' % (a)
            txbaudot(b)
   
def txbaudot(c):
  """
  transmit one character to the teletype
  """

  #here
  global pi
  gpio=2
  #print(c)
  #motor_start()

  pi.wave_clear()
  wf=[]
  micros = gpio8period*1000

  wf.append(pigpio.pulse(0, 1<<gpio, 20000))

  for b in reversed(c):
    if (int(b) == 1):
      wf.append(pigpio.pulse(1<<gpio, 0, micros))
    else:
      wf.append(pigpio.pulse(0, 1<<gpio, micros))

  wf.append(pigpio.pulse(1<<gpio, 0, micros))
  pi.wave_add_generic(wf)

  wid = pi.wave_create()

  if wid >= 0:
    pi.wave_send_once(wid)

  while pi.wave_tx_busy():
    time.sleep(0.2)

  #timer was .1 / .07
  time.sleep(.05)

def txbin(s):
  txbaudot(s)

def tx_keycode(s):
  #print 'tx_keycode(%s)' % (s)
  k = int(s)
  if (ascii_to_baudot_char.has_key(chr(k))):
      a = ascii_to_baudot_char[chr(k)]
      #print 'ascii_to_baudot_char(%d): %s' % (i,a)
      if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
        b = ascii_to_binstr[a]
        #print 'tx_keycode() %d (%s) -> (%s)' % (k,chr(k),b)
        if (b != '00000'):
          #print 'tx_keycode(%s)' % (b)
          txbaudot(b)

shifted = False

def update_column_position():
  """
  keep track of column position so we can insert cr lf when necessary
  """
  global ColumnCurrentPosition, ColumnMax
  ColumnCurrentPosition = ColumnCurrentPosition + 1
  if ColumnCurrentPosition > ColumnMax:
    #print "update_column_position(): col 0"
    tx_ctl('cr')
    tx_ctl('lf')
    ColumnCurrentPosition = 0; 
    #print "column reset to 0"

def shift_up():
  """
  Shift up to figures
  """
  global shifted
  if not shifted:
    tx_ctl('figs')
    shifted = True

def shift_down():
  """
  Shift down to letters
  """
  global shifted
  if shifted:
    tx_ctl('ltrs')
    shifted = False


def tx_ascii_chr(c):
  """
  send an ascii character
  """
  if (ascii_to_baudot_char.has_key(c)):
      a = ascii_to_baudot_char[c]
      #print 'ascii_to_baudot_char(%d): %s' % (i,a)
      if (ascii_to_binstr.has_key(a)): # and 2nd reduce mapping table has key
        b = ascii_to_binstr[a]
        if (b != '00000'):
          #print 'tx_ascii_chr(%s)' % (b)
          if (a in needs_shift_up):
            shift_up()
          else:
            shift_down()
          txbaudot(b)
          update_column_position()



def tx(c):
  """
  send an ascii character
  """
  tx_keycode(c)

def tx_str(s):
  """
  transmit an ascii string
  """
  de_uried_str = urllib.unquote(s)
  for i in range(len(de_uried_str)):
    #print '[%s]' % de_uried_str[i]
    tx_ascii_chr(de_uried_str[i])


def tx_ctl(c):
  """
  transmit a control code 'lf' = line feed, 'cr' = carriage return, etc.
  """
  global ColumnCurrentPosition
  #print "tx_ctl(%s)" % c
  if (c == 'cr'):
    txbaudot('01000')
    ColumnCurrentPosition = 0
  elif (c == 'lf'):
    txbaudot('00010')
  elif (c == 'figs'):
    txbaudot('11011')
  elif (c == 'ltrs'):
    txbaudot('11111')
  elif (c == 'bell'):
    txbaudot('11011') # shift up
    txbaudot('00101')
    txbaudot('11111') # shift down
    txbaudot('01000') # cr
    txbaudot('00100') # space
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('00100')
    txbaudot('01000') # cr
    ColumnCurrentPosition = 0
  elif (c == 'null'):
    txbaudot('00000')
  elif (c == 'space'):
    txbaudot('00100')
    update_column_position()

init()

FILE_NAME = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    #print('retrieving and replying to tweets...', flush=True)
    # DEV NOTE: use 1060651988453654528 for testing.
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    # NOTE: We need to use tweet_mode='extended' below to show
    # all full tweets (with full_text). Without it, long tweets
    # would be cut off.
    mentions = api.mentions_timeline(
                        last_seen_id,
                        tweet_mode='extended')
    for mention in reversed(mentions):
        #print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        init()
        tx_str(mention.full_text)
        init()
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if '#tweetateletype' in mention.full_text.lower():
            #print('found the magic word!', flush=True)
            #print('responding back...', flush=True)
            api.update_status('@' + mention.user.screen_name +
                    '#Howdy do back to you!', mention.id)

while True:
    reply_to_tweets()
    time.sleep(15)
