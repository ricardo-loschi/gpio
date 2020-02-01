#!/usr/bin/python

import os
from flask import Flask, abort, request, jsonify, g, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask_api import FlaskAPI
import RPi.GPIO as GPIO

GPIOS = {"room1": 12, "room2": 16,"room3": 18,"kitchen": 22,"livingroom": 12}
GPIO.setmode(GPIO.BOARD)
GPIO.setup(GPIOS["room1"], GPIO.OUT)
GPIO.setup(GPIOS["room2"], GPIO.OUT)
GPIO.setup(GPIOS["room3"], GPIO.OUT)
GPIO.setup(GPIOS["kitchen"], GPIO.OUT)
GPIO.setup(GPIOS["livingroom"], GPIO.OUT)

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
    return {color: GPIO.input(GPIOS[color])}

@app.route('/gpio/states/<pino>/', methods=["GET"])
def api_GPIOS_control_states(pino):
	return {"state": GPIO.input(GPIOS[pino])}

if __name__ == "__main__":
    app.run(host='0.0.0.0')
