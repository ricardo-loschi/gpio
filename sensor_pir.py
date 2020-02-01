import RPi.GPIO as GPIO
import time,threading
from threading import Thread
import termios, fcntl, sys, os
import requests
import json


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(36,GPIO.IN)
GPIO.setup(12,GPIO.OUT)
GPIO.output(12,1)

def send_notification():
 header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic NGZhOTBiNWYtMzMyZC00ZjRkLWFhOTMtOGQ2ZGFkZDA1ZTAy"}

 payload = {"app_id": "da410000-4f23-47e5-890e-f22beb3859cb",
           "included_segments": ["All"],
           "contents": {"en": "Alarme disparado!!"}}
 
 req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
 
 print(req.status_code, req.reason)

'''
def lendo_pir():
 global dead
 while (not dead):
  i=GPIO.input(36)
  alarmesetado = GPIO.input(12) 
  if i==0:
   print "Sem Movimento"
   #if alarmesetado == 1: 
   #  GPIO.output(12,1) 
   time.sleep(0.1)
  elif i==1: 
   print "Movimentacao"
   count=0
   tempo_entrada = 10
   tecla='a'

   while count <= tempo_entrada and tecla != '2':
    print ("Tempo de entrada " + str(count) + " segundos") 
    time.sleep(1)
    count=count+1
   if tecla != '2':
    GPIO.output(12,0)
    time.sleep(0.1)
   else:
    GPIO.output(12,1)
    time.sleep(0.4)
    GPIO.output(12,0)
    time.sleep(0.4)
    GPIO.output(12,1)
 
thread_alarme=Thread(target=lendo_pir)
'''
opcao=0
#global dead
#dead =False
while (opcao!=3):
 GPIO.output(12,1)
 opcao=input("1-Ligar alarme \n2-Desligar alarme\n3-sair\n")
 if (opcao==1):
  print "Ativando alarme"
  GPIO.output(12,1)
  time.sleep(0.4)
  GPIO.output(12,0)
  time.sleep(0.4)
  GPIO.output(12,1)
  tempo_saida=10
  i=1
  while i <= tempo_saida:
    print('Tempo de saida '+ str(i)+ ' segundos')
    time.sleep(1)
    i=i+1
  print("Alarme ativado") 
  sair=False
  while (not sair):
   i=GPIO.input(36)
   alarmesetado = GPIO.input(12)
   if i==1:
    print "Movimentacao"
    count=1
    tempo_entrada = 10
    tecla='a'
    
    fd = sys.stdin.fileno()
  
    oldterm = termios.tcgetattr(fd)
    newattr = termios.tcgetattr(fd)
    newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
    termios.tcsetattr(fd, termios.TCSANOW, newattr)

    oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

    try:
     while tecla != "2" and count<=tempo_entrada:
        print ("Tempo de entrada " + str(count) + " segundos")
        time.sleep(1)
        count=count+1
        try:
            tecla = sys.stdin.read(1)
            print "Got character", repr(tecla)
            if tecla == "2":
             break
        except IOError: pass
    finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    if tecla != '2':
     GPIO.output(12,0)
     time.sleep(0.1)
     print("Sirene Ativada!!!!!")
     #send_notification()
     fd = sys.stdin.fileno()

     oldterm = termios.tcgetattr(fd)
     newattr = termios.tcgetattr(fd)
     newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
     termios.tcsetattr(fd, termios.TCSANOW, newattr)

     oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
     fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

     try:
      while tecla != "2": 
        time.sleep(1)
        count=count+1
        try:
            tecla = sys.stdin.read(1)
            print "Got character", repr(tecla)
            if tecla == "2":
             GPIO.output(12,1)
             time.sleep(0.4)
             print("Sirene desativada!!!!")
             sair=True 
             break
        except IOError: pass
     finally:
        termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
    else:
     GPIO.output(12,1)
     time.sleep(0.4)
     sair=True

 if (opcao==2):
  dead=True   
  GPIO.output(12,1)
  time.sleep(0.4)
  GPIO.output(12,0)
  time.sleep(0.4)
  GPIO.output(12,1)
  print "Alarme desativado"
