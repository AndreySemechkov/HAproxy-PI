#!/usr/bin/env python
from random import *
import requests

def genRandIntsList(maxNum, missionsNum):
    rand = []
    for i in range(0, missionsNum):
        rand.append(randint(1, maxNum))
    return rand

def httpPOST(numList):
    # defining the api-endpoint
    destURL = "http://httpbin.org/post"
#send the random numbers one by one as jobs
    for num in numList:
        numDict = {}
        numDict[num] = num
        #request = requests.post(url=destURL, data=numDict)
        request = requests.get('http://192.168.56.254/cgi-bin/hello.cgi')
        print(request.text)

randIntsList = genRandIntsList(10,10)
httpPOST(randIntsList)

