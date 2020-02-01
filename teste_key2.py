import termios, fcntl, sys, os

while 1:
        try:
            c = sys.stdin.read(1)
            print "Got character", repr(c)
            if c == "q":
             break
        except IOError: pass

