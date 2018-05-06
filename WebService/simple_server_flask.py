#!/usr/bin/env python

from flask import Flask, url_for
import math
app = Flask(__name__)

@app.route('/')
def index():
    return 'Welcome to Load Balancing project :)'

@app.route('/power/<int:num>')
def calc_power(num):
    return '%d' %(num*num)
	
@app.route('/prime/<int:numOrig>')
def closest_prime(numOrig):
	num = int(str(numOrig)[0:6])
	for i in range(num, 1, -1):
		isPrime = True
		for j in range(2, int(math.ceil(math.sqrt(i)))):
			if i % j == 0:
				isPrime = False
		if isPrime:
			return 'Hello Slowpoke, Original request: %d\nAltered number: %d\nThe result: %d' % (numOrig, num, i)
	
with app.test_request_context():
	print url_for('index')
	print url_for('calc_power', num='2')
	print url_for('closest_prime', numOrig='2')

app.run(host="0.0.0.0", port=80, debug=True)
