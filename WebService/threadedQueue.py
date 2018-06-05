import threading
import time
import logging
import random
import Queue
import math

logging.basicConfig(level=logging.DEBUG,
					format='(%(threadName)-9s) %(message)s', )


def genFixedDigitsRand(n):
	range_start = 10**(n-1)
	range_end = (10**n)-1
	return random.randint(range_start, range_end)


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
		return str(self.numOfReq) + ". Result for num: " + str(self.reqNum) + \
								 "  Delay: " + str(self.delay()) + \
								 "  Calc Time: " + str(self.calcTime()) + \
								 "  Total Time: " + str(self.totalTime()) + \
								 "         Start: " + str(self.timeS) + "     Finish: " + str(self.timeF)

	def calcTime(self):
		if self.timeS is not None and self.timeF is not None:
			return self.timeF-self.timeS
		return None

	def delay(self):
		return self.timeS - self.reqTime

	def totalTime(self):
		return self.timeF - self.reqTime


def closestPrime(qin, qout):
	while(True):
		req = qin.get()
		res = Result(req.numOfReq, req.time ,req.num)
		# -1 indicates EOF
		if req.num == -1:
			qout.put(Result(req.numOfReq,-1,-1))
			logging.debug('Done')
			return
		for i in range(req.num, 1, -1):  # iterate backwards
			isPrime = True
			for j in range(2, int(math.ceil(math.sqrt(i)))):
				if i % j == 0:
					isPrime = False
			if isPrime:
				res.timeF = time.time()
				break
		qout.put(res)
		logging.debug(res)



if __name__ == '__main__':
	qin = Queue.Queue()
	qout = Queue.Queue()


	"""create worker thread - waits for requests in qin (pops one request at a time - blocking)"""
	t = threading.Thread(target=closestPrime, args=(qin,qout,))
	t.start()

	"""insert 100 random numbers in random frequency"""
	for i in range(10):
		time.sleep(random.random())
		req = Request(genFixedDigitsRand(8))
		logging.debug(req)
		qin.put(req)



	qin.put(Request(-1))

	logging.debug('Waiting for closestPrime thread')
	main_thread = threading.currentThread()
	# for t in threading.enumerate():
	#     if t is not main_thread:
	t.join()
	logging.debug('Primes calculated: %d', qout.qsize())