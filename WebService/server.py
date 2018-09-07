#!/usr/bin/env python
import web
import sys
import math
import Queue
import threading
import time
import logging


logging.basicConfig(level=logging.DEBUG,
					format='(%(threadName)-9s) %(message)s', )


class Request(object):
	counter = 1

	def __init__(self, num):
		self.time = time.time()
		self.numOfReq = Request.counter
		Request.counter += 1
		self.num = num

	def __str__(self):
		return str(self.numOfReq) + ". Request - " + str(self.num) + "               " + str(self.time)


class Result(object):

	def __init__(self,numOfReq, reqTime, reqNum, timeF=None):
		self.timeS = time.time()
		self.numOfReq = numOfReq
		self.reqNum = reqNum
		self.reqTime = reqTime
		self.timeF = timeF


	def __str__(self):
		if self.reqNum == -1:
			return "Done!"
		return str(self.numOfReq) + ". Result for num: " + str(self.reqNum) + \
								 "  Delay: " + str(self.delay()) + \
								 "  Calc Time: " + str(self.calcTime()) + \
								 "  Total Time: " + str(self.totalTime()) + \
								 "         Start: " + str(self.timeS) + "     Finish: " + str(self.timeF) + "\n"

	def calcTime(self):
		if self.timeS is not None and self.timeF is not None:
			return self.timeF-self.timeS
		return None

	def delay(self):
		return self.timeS - self.reqTime

	def totalTime(self):
		return self.timeF - self.reqTime

load = sys.argv[1]
qin = Queue.Queue()
qout = Queue.Queue()
init = False

def initializeWorker():
	t = threading.Thread(target=closestPrime)
	t.start()


def closestPrime():
	while(True):
		req = qin.get()
		res = Result(req.numOfReq, req.time ,req.num)
		# -1 indicates EOF
		if req.num == -1:
			qout.put(Result(req.numOfReq,-1,-1))
			logging.debug('Done')
			return
		num = int(str(req.num)[0:int(load)])
		for i in range(num, 1, -1):  # iterate backwards
			isPrime = True
			for j in range(2, int(math.ceil(math.sqrt(i)))):
				if i % j == 0:
					isPrime = False
			if isPrime:
				res.timeF = time.time()
				break
		qout.put(res)
		logging.debug(res)


# we can choose the port number we monitor
class MyApplication(web.application):
	def run(self, port=80, *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, ('0.0.0.0', port))


urls = (
	'/isPrime/(-?\d+)', 'isPrime',
	'/now', 'get_post2',
)


class isPrime:

	def GET(self,num):
		if not init:
			initializeWorker()
		num = int(u'{0}'.format(num))
		req = Request(num)
		logging.debug('***********************************************************************************')
		logging.debug(req)
		qin.put(req)
		logging.debug("New queue size is: " + str(qin.qsize()))
		logging.debug('***********************************************************************************')
		try:
			res = "This is Slowpoke\n" + str(qout.get())
			#while(qout.qsize()):
			#	res += "This is Usain\n" + str(qout.get())
		except Queue.Empty, e:
			res = "This is Slowpoke - The result took too long to calc"	
		return res


	def POST(self):

		session_args = web.data()
		print session_args


class get_post2:


	def GET(self):

		return "Hello! I'm Slowpoke, want to be friends?"

	def POST(self):

		session_args = web.data()
		print session_args

if __name__ == "__main__":
	app = MyApplication(urls, globals())
	app.run()
