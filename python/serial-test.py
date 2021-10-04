import serial
import subprocess
import time

socat=subprocess.Popen(["/usr/bin/socat", "-d", "-d", "pty,raw,echo=0", "pty,raw,echo=0,link=/dev/teletype"])
time.sleep(3)
s = serial.Serial('/dev/pts/7',baudrate=9600,timeout=1)
query="query\n"
while True:
   s.write(query.encode())
   resp = s.read()
   if resp: print(resp)
