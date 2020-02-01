import termios, fcntl, sys, os
import time
fd = sys.stdin.fileno()

oldterm = termios.tcgetattr(fd)
newattr = termios.tcgetattr(fd)
newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
termios.tcsetattr(fd, termios.TCSANOW, newattr)

oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)
c="0"
i=1
try:
    while i<10 and c!="q":
        print (str(i)+" seguntos") 
        time.sleep(1)
        i=i+1
        try:
            c = sys.stdin.read(1)
            print "Got character", repr(c)
            if c == "q":
             break 
        except IOError: pass
finally:
    termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
