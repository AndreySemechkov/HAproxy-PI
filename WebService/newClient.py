#!/usr/bin/env python
from random import *
import time
import grequests
import requests
import json
import threading
import sys

NUM_OF_THREADS = 50
REQ_PER_THREAD = 1000

threadsList = []
response_list = [None] * (NUM_OF_THREADS * REQ_PER_THREAD)


"""
Generates a random number with n digits
"""
def genFixedDigitsRand(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)

"""
Sends REQ_PER_THREAD requests using httpGET() function. the parameter for each request is a randomly generated number
When the response received, it is stored in a list for further analysis
"""
def myThread(id):
    for i in range(REQ_PER_THREAD):
        response_list[id * REQ_PER_THREAD + i] = httpGET(genFixedDigitsRand(5))


"""
Creates NUM_OF_THREADS threads in the system when each thread is myThread
"""
def initializeWorkers():
    print "Creating threads..."
    for t_id in range(NUM_OF_THREADS):
        threadsList.append(threading.Thread(target=myThread, kwargs={"id": t_id}))
    print "Threads were created successfully!\n"

    print "Starting threads..."
    for t_id in range(NUM_OF_THREADS):
        threadsList[t_id].start()
    print "Threads were started successfully!\n"


def joinAllThreads():
    print "Joining threads..."
    for t_id in range(NUM_OF_THREADS):
        threadsList[t_id].join()
        print "Thread #" + str(t_id) + " was joined successfully!"


"""
Sends HTTP get request to "http://192.168.56.254/isPrime/" URL with randNum parameter
"""
def httpGET(randNum):
    destURL = "http://192.168.56.254/isPrime/" + str(randNum)  # defining the api-endpoint
    request = requests.get(destURL)
    return request


start = time.time()
print "Executing client ..."

initializeWorkers()
joinAllThreads()

totalTime = time.time() - start

print "*******************"

errors = 0

for response in response_list:
    if response.status_code != 200:
        errors += 1

fileName = str(sys.argv[1]) + '_T' + str(totalTime) + '_E' + str(errors) + '.csv'
csv = open(fileName, 'w')

for key, value in json.loads(response_list[0].text).iteritems():
    csv.write(key + ", ")

for response in response_list:
    if response.status_code == 200:
        csv.write("\n")
        for key, value in json.loads(response.text).iteritems():
            csv.write(str(value) + ", ", )

csv.close()
print "Total errors: " + str(errors)
print "Total time: " + str(totalTime)
