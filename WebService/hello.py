#!/usr/bin/env python
'''
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

'''


import web


# we can choose the port number we monitor
class MyApplication(web.application):
    def run(self, port=80, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


urls = (
    '/hi', 'get_post',
    '/now', 'get_post2',	
)


class get_post:


    def GET(self):

        return "Hi Jenny! My name is ***Slowpoke** \n I was sent just to tell you that We fixed our app issue!"

    def POST(self):

        session_args = web.data()
        print session_args


class get_post2:


    def GET(self):

        return "Now i will try to use the proxy with the numbers generation"

    def POST(self):

        session_args = web.data()
        print session_args

if __name__ == "__main__":
    app = MyApplication(urls, globals())
    app.run()
