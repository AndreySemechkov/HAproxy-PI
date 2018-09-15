#!/usr/bin/env python
from random import *
import time
import grequests
import json


# def genRandIntsList(maxNum, missionsNum):
#    rand = []
#    for i in range(0, missionsNum):
#        rand.append(randint(1, maxNum))
#    return rand

def genFixedDigitsRand(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
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
    # return json.loads(response.content)


def httpGET(randNum):
    destURL = "http://localhost:8080/isPrime/" + str(randNum)  # defining the api-endpoint
    # destURL = "http://192.168.56.254/isPrime/" + str(randNum) # defining the api-endpoint
    #    action_item = grequests.get(destURL, hooks = {'response' : do_something})
    action_item = grequests.get(destURL)
    async_list.append(action_item)


#    print request.text
# destURL = "http://httpbin.org/get"
# destURL = "http://192.168.56.254/cgi-bin/hello.cgi"
# send the random numbers one by one as jobs
# request = requests.post("http://192.168.56.254/cgi-bin/hello.cgi", data={'foo': 'bar'})
# request = requests.post(url=destURL, data=numDict)


start = time.time()
print "Executing client ..."
for i in range(100):
    httpGET(genFixedDigitsRand(5))

rs = grequests.map(async_list)

suc = []
fail = []
for response in rs:
    if response.status_code == 200:
        suc.append(response.content)
    else:
        fail.append(response.content)

d = list(map(lambda s: json.loads(s), suc))
s = sorted(d, key=lambda k: k['timeRequestReceived'])
# f = list(map(lambda j: json.dumps(j), s))

csv = open('t.csv', 'a')
for key, value in s[0].iteritems():
    csv.write(key + ", ")

for d in s:
    csv.write("\n")
    for key, value in d.iteritems():
        csv.write(str(value) + ", ", )
csv.close()

print "Timed out requests count: " + str(len(fail))
for f in fail:
    print f
"""
for j in f:
	print j
	
print
print
print "&&&&&&&&&&&&&"	

print "&&&&&&&&&&&&&"


#s = sorted(rs, key=lambda k: k['timeRequestReceived'])
#for response in list(map(lambda j: json.dumps(j), s)):

for response in rs:
    #print(response)
    print(response.content)
"""
print
print(time.time() - start)
