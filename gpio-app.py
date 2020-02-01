#!/usr/bin/python

from flask import request
from flask_api import FlaskAPI
import RPi.GPIO as GPIO

GPIOS = {"room1": 16, "room2": 15,"room3": 18,"kitchen": 12,"livingroom": 24}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIOS["room1"], GPIO.OUT)
GPIO.setup(GPIOS["room2"], GPIO.OUT)
GPIO.setup(GPIOS["room3"], GPIO.OUT)
GPIO.setup(GPIOS["kitchen"], GPIO.OUT)
GPIO.setup(GPIOS["livingroom"], GPIO.OUT)

app = FlaskAPI(__name__)

@app.route('/', methods=["GET"])
def api_root():
    return {
           "gpio_url": request.url + "gpio/(room1 | room2 | room3 | kitchen | livingroom)/",
      		 "gpio_url_POST": {"state": "(0 | 1)"}
    			 }
  
@app.route('/gpio/<color>/', methods=["GET", "POST"])
def api_GPIOS_control(color):
    if request.method == "POST":
        if color in GPIOS:
            GPIO.output(GPIOS[color], int(request.data.get("state")))
    return {color: GPIO.input(GPIOS[color])}

if __name__ == "__main__":
    app.run(host='0.0.0.0')
