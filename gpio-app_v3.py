#!/usr/bin/python

import Adafruit_DHT
import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_api import FlaskAPI
import RPi.GPIO as GPIO
import pygame
import os
import time,threading
from threading import Thread
import requests
import json

tempo_entrada=10
tempo_saida=10
GPIOS = {"sensor_pir1":16,"sensor_pir2":36,"siren_relay":12,"room1":18,"room2":38,"room3":32,"gpio_alarme_pir1":37,"gpio_alarme_pir2":35}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIOS["room1"], GPIO.OUT)
GPIO.setup(GPIOS["room2"], GPIO.OUT)
GPIO.setup(GPIOS["room3"], GPIO.OUT)
GPIO.setup(GPIOS["siren_relay"], GPIO.OUT)
GPIO.setup(GPIOS["sensor_pir1"], GPIO.IN)
GPIO.setup(GPIOS["sensor_pir2"], GPIO.IN)
GPIO.setup(GPIOS["gpio_alarme_pir1"], GPIO.OUT)
GPIO.setup(GPIOS["gpio_alarme_pir2"], GPIO.OUT)
GPIO.output(GPIOS["siren_relay"], 1)

# initialization
app = FlaskAPI(__name__)

# initialization
#app1 = FlaskAPI(__name__)
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201,
             {'Location': url_for('get_user', id=user.id, _external=True)})

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})


@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api/resource')
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/', methods=["GET"])
def api_root():
    return {
           "gpio_url": request.url + "gpio/(room1 | room2 | room3 | kitchen | livingroom)/",
      		 "gpio_url_POST": {"state": "(0 | 1)"}
    			 }
  
@app.route('/gpio/<color>/', methods=["GET", "POST"])
@auth.login_required
def api_GPIOS_control(color):
    if request.method == "POST":
        if color in GPIOS:
            GPIO.output(GPIOS[color], int(request.data.get("state")))
    if color !="siren_relay":  
     return {color: GPIO.input(GPIOS[color])}
    else:
     if GPIO.input(GPIOS[color]) == 1:
      return {color: 0}
     else:
      return {color: 1}

@app.route('/gpio/gpio_alarme/', methods=["GET", "POST"])
@auth.login_required
def api_gpio_alarme():
    if request.method == "POST":
     GPIO.output(GPIOS["gpio_alarme_pir1"], int(request.data.get("state")))
     play_sound('alarme.mp3')
    return {"gpio_alarme_pir1": GPIO.input(GPIOS["gpio_alarme_pir1"])}

@app.route('/gpio/states/<pino>/', methods=["GET"])
def api_GPIOS_control_states(pino):
	return {"state": GPIO.input(GPIOS[pino])}

@app.route('/gpio/temperatura/', methods=["GET"])
def api_GPIOS_temperatura():
# GPIO.setup(25, GPIO.OUT)
 sensor = Adafruit_DHT.DHT11
 umid, temp = Adafruit_DHT.read_retry(sensor, 25);
 if temp is None:
  temp=0
 return {"temperatura":temp }

@app.route('/gpio/umidade/', methods=["GET"])
def api_GPIOS_umidade():
# GPIO.setup(25, GPIO.OUT)
 sensor = Adafruit_DHT.DHT11
 umid, temp = Adafruit_DHT.read_retry(sensor, 25);
 if temp is None:
  temp=0
 return {"umidade":umid }

@app.route('/gpio/sensor_info/', methods=["GET"])
def api_GPIOS_sensor_info():
# GPIO.setup(25, GPIO.OUT)
 sensor = Adafruit_DHT.DHT11
 umid, temp = Adafruit_DHT.read_retry(sensor, 25);
 if temp is None:
  temp=0
 return {"umidade":str(umid),"temperatura":str(temp)}

@app.route('/gpio/ler_sensor/<sensor>/', methods=["GET","POST"])
def api_GPIOS_ler_sensor(sensor): 
 if request.method == "POST":
  GPIO.output(GPIOS[sensor],int(request.data.get("state")))
  if int(request.data.get("state")) == 1:
   thread_alarme=Thread(target=lendo_sensor, args=(sensor,))
   if thread_alarme.is_alive() == False: 
    thread_alarme.start()
 return {sensor: GPIO.input(GPIOS[sensor])}

def lendo_sensor(sensor):
 status=GPIO.input(GPIOS[sensor]) 
 print("Contagem de tempo para saida....")
 count=tempo_saida
 while count>=0:
  print(str(count)+" segundos...")
  count=count-1
  time.sleep(1)
 
 while (status == 1):
   status=GPIO.input(GPIOS[sensor])
   date_now=time.strftime("%c")
   nome_sensor = 'sensor_'+sensor[-4:]
   print("["+date_now+"] Alarme do sensor "+nome_sensor+" setado para ler.....")   
   i=GPIO.input(GPIOS[nome_sensor])
   time.sleep(0.3)
   if i==1:
    date_now=time.strftime("%c")
    print ("Movimentacao ["+date_now+"]")
    print ("Contagem de tempo para entrada....")
    count=tempo_entrada
    while count>=0 and status == 1:
     print (str(count)+" segundos...")
     count=count-1
     status=GPIO.input(GPIOS[sensor])
     time.sleep(1)
    if status == 1:
     msg = "Alarme disparado!\n["+nome_sensor+"]\nSirene Ativada!\n["+date_now+"]"
     print (msg)
     send_notification(msg)
     while status == 1:
       status=GPIO.input(GPIOS[sensor])
       if status == 0:
        print("Alarme desativado! Sirene desligada")
 
   time.sleep(3)

def play_sound(file_name):
 # Inicializando o PyGame
 pygame.init()

 # Carregando o arquivo MP3 e executando
 if os.path.exists(file_name):
    pygame.mixer.music.load(file_name)
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(4)

    clock = pygame.time.Clock()
    clock.tick(10)

 else:
    print('O arquivo ' + file_name +' nao esta no diretorio do script Python')

def send_notification(message):
 header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": "Basic NGZhOTBiNWYtMzMyZC00ZjRkLWFhOTMtOGQ2ZGFkZDA1ZTAy"}

 payload = {"app_id": "da410000-4f23-47e5-890e-f22beb3859cb",
           "included_segments": ["All"],
           "contents": {"en": message}}

 req = requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))

 print(req.status_code, req.reason)

   
if __name__ == "__main__":
 print ("House Protection V2 by BITTEC Tecnologia da Informacao ")
 app.run(host='0.0.0.0') 
