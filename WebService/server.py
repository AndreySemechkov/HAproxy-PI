#!/usr/bin/env python


import web
import sys
import math

load = sys.argv[1]

def closest_prime(numOrig):
	num = int(str(numOrig)[0:load])
	for i in range(num, 1, -1):
		isPrime = True
		for j in range(2, int(math.ceil(math.sqrt(i)))):
			if i % j == 0:
				isPrime = False
		if isPrime:
			return 'Hello Slowpoke, Original request: %d\nAltered number: %d\nThe result: %d' % (numOrig, num, i)
 

# we can choose the port number we monitor
class MyApplication(web.application):
    def run(self, port=80, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


urls = (
    '/isPrime/(\d+)', 'isPrime',
    '/now', 'get_post2',	
)


class isPrime:

    def GET(self,num):
	
	num = u'{0}'.format(num)
	res = closest_prime(int(num))
	print '***********************************************************************************' 	
	print res
	print '***********************************************************************************' 
	return res
 
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
