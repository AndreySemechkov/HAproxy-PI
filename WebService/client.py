#!/usr/bin/env python
from random import *
import time
import grequests

#def genRandIntsList(maxNum, missionsNum):
#    rand = []
#    for i in range(0, missionsNum):
#        rand.append(randint(1, maxNum))
#    return rand

def genFixedDigitsRand(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)
"""
def httpGET(randNum):
    destURL = "http://192.168.56.254/isPrime/" + str(randNum) # defining the api-endpoint
    request = requests.get(destURL)
    print request.text
    #destURL = "http://httpbin.org/get"
    #destURL = "http://192.168.56.254/cgi-bin/hello.cgi"
	#send the random numbers one by one as jobs
	#request = requests.post("http://192.168.56.254/cgi-bin/hello.cgi", data={'foo': 'bar'})        
	#request = requests.post(url=destURL, data=numDict)
"""
async_list = []

# A simple task to do to each response object
def do_something(response):
    return response


def httpGET(randNum):
    destURL = "http://192.168.56.254/isPrime/" + str(randNum) # defining the api-endpoint
#    action_item = grequests.get(destURL, hooks = {'response' : do_something})
    action_item = grequests.get(destURL)
    async_list.append(action_item)
#    print request.text
    #destURL = "http://httpbin.org/get"
    #destURL = "http://192.168.56.254/cgi-bin/hello.cgi"
	#send the random numbers one by one as jobs
	#request = requests.post("http://192.168.56.254/cgi-bin/hello.cgi", data={'foo': 'bar'})        
	#request = requests.post(url=destURL, data=numDict)


start = time.time()
#for i in range(1, 100):
for i in range(100):
    randNum = genFixedDigitsRand(5)
    httpGET(randNum)
     #httpGET(int(str(i)*10))
for item in async_list:
    print item
rs = grequests.map(async_list) 
for response in rs:
    print(response.content)
print(time.time()-start)
