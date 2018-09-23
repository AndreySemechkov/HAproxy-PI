#!/usr/bin/env python
import web
import sys
import math
import Queue
import threading
import time
import logging
import json

logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s', )

currServerName = "server"+sys.argv[3]


def jsonDefault(OrderedDict):
    return OrderedDict._dict_


class Request(object):
    counter = 1

    def _init_(self, num):
        self.time = time.time()
        self.requestNum = Request.counter
        Request.counter += 1
        self.num = num

    def _str_(self):
        return str(self.requestNum) + ". Request - " + str(self.num) + "               " + str(self.time)


class Result(object):

    def _init_(self, numOfReq, reqTime, reqNum, timeF=None):
        self.ServerName = currServerName
        self.timeStartedCalc = time.time()
        self.requestNum = numOfReq
        self.numToCalc = reqNum
        self.timeRequestReceived = reqTime
        self.timeFinishedCalc = timeF
        self.totalHandlingTime = None

    def _str_(self):
        if self.numToCalc == -1:
            return "Done!"
        # return str(self.requestNum) + ". Result for num: " + str(self.numToCalc) + \
        # 						 "  Delay: " + str(self.delay()) + \
        # 						 "  Calc Time: " + str(self.calcTime()) + \
        # 						 "  Total Time: " + str(self.totalTime()) + \
        # 						 "         Start: " + str(self.timeStartedCalc) + "     Finish: " + str(self.timeFinishedCalc) + "\n"
        return json.dumps(self, default=jsonDefault, indent=4)

    def calcTime(self):
        if self.timeStartedCalc is not None and self.timeFinishedCalc is not None:
            return self.timeFinishedCalc - self.timeStartedCalc
        return None

    def delay(self):
        return self.timeStartedCalc - self.timeRequestReceived

    def updateTotalTime(self):
        self.totalHandlingTime = self.timeFinishedCalc - self.timeRequestReceived


load = sys.argv[1]
port = sys.argv[2]
qin = Queue.Queue()
qout = Queue.Queue()
init = False


def initializeWorker():
    t = threading.Thread(target=closestPrime)
    t.start()


def closestPrime(req):
    while (True):
        #req = qin.get()
        res = Result(req.requestNum, req.time, req.num)
        # -1 indicates EOF
        if req.num == -1:
            qout.put(Result(req.requestNum, -1, -1))
            logging.debug('Done')
            return
        num = int(str(req.num)[0:int(load)])
        for i in range(num, 1, -1):  # iterate backwards
            isPrime = True
            for j in range(2, int(math.ceil(math.sqrt(i)))):
                if i % j == 0:
                    isPrime = False
            if isPrime:
                res.timeFinishedCalc = time.time()
                break
        res.updateTotalTime()
        #qout.put(res)
        logging.debug(res)
	return res


# we can choose the port number we monitor
class MyApplication(web.application):
    def run(self, port=int(port), *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))


urls = (
    '/isPrime/(-?\d+)', 'isPrime',
    '/now', 'get_post2',
)


class isPrime:

    def GET(self, num):
        #if not init:
            #initializeWorker()
        num = int(u'{0}'.format(num))
        req = Request(num)
        logging.debug('*****************************')
        logging.debug(req)
        #qin.put(req)
        logging.debug("New queue size is: " + str(qin.qsize()))
        logging.debug('*****************************')
        try:
	    res = str(closestPrime(req))
            #res = str(qout.get())
            # res = "This is " + currServerName + "\n" + str(qout.get())
        # while(qout.qsize()):
        #	res += "This is Usain\n" + str(qout.get())
        except Queue.Empty, e:
            res = "This is " + currServerName + " - The result took too long to calc"
        return res

    def POST(self):

        session_args = web.data()
        print session_args


class get_post2:

    def GET(self):
        return "Hello! I'm " + currServerName + ", want to be friends?"

    def POST(self):
        session_args = web.data()
        print session_args


if _name_ == "_main_":
    app = MyApplication(urls, globals())
    app.run()
