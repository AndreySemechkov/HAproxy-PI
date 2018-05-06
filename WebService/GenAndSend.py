#!/usr/bin/env python
from random import *
import requests
import time

#def genRandIntsList(maxNum, missionsNum):
#    rand = []
#    for i in range(0, missionsNum):
#        rand.append(randint(1, maxNum))
#    return rand

def genFixedDigitsRand(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def httpGET(randNum):
    destURL = "http://192.168.56.254/" + randNum# defining the api-endpoint
    request = requests.get(destURL)
    print request.text
    #destURL = "http://httpbin.org/get"
    #destURL = "http://192.168.56.254/cgi-bin/hello.cgi"
	#send the random numbers one by one as jobs
	#request = requests.post("http://192.168.56.254/cgi-bin/hello.cgi", data={'foo': 'bar'})        
	#request = requests.post(url=destURL, data=numDict)


start = time.time()
for i in range(1000):
    randNum = genFixedDigitsRand(12)
    httpGET(randNum)
print(time.time()-start)
