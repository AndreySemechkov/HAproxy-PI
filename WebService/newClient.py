#!/usr/bin/env python
from random import *
import time
import grequests
import requests
import json
import threading


NUM_OF_THREADS = 50
REQ_PER_THREAD = 1000

threadsList = []
response_list = [None] * (NUM_OF_THREADS * REQ_PER_THREAD)

def genFixedDigitsRand(n):
    range_start = 10 ** (n - 1)
    range_end = (10 ** n) - 1
    return randint(range_start, range_end)


def myThread(id):
    for i in range(REQ_PER_THREAD):
        httpGET(genFixedDigitsRand(5))
        response_list[id*REQ_PER_THREAD + i] = httpGET(genFixedDigitsRand(5))


def initializeWorkers():
    print "Creating threads..."
    for t_id in range(NUM_OF_THREADS):
        threadsList.append(threading.Thread(target=myThread, kwargs={"id":t_id}))
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


def httpGET(randNum):
    # destURL = "http://localhost:8080/isPrime/" + str(randNum)  # defining the api-endpoint
    destURL = "http://192.168.56.254/isPrime/" + str(randNum)  # defining the api-endpoint
    request = requests.get(destURL)
    return request.text



start = time.time()
print "Executing client ..."

initializeWorkers()
joinAllThreads()

print "*******************"

csv = open('t.csv', 'w')
for key, value in json.loads(response_list[0]).iteritems():
    csv.write(key + ", ")

for response in response_list:
    csv.write("\n")
    for key, value in json.loads(response).iteritems():
        csv.write(str(value) + ", ", )
csv.close()



# suc = []
# fail = []
# for response in response_list:
#     if response.status_code == 200:
#         suc.append(response.content)
#     else:
#         fail.append(response.content)

# d = list(map(lambda s: json.loads(s), suc))
# s = sorted(d, key=lambda k: k['timeRequestReceived'])
# f = list(map(lambda j: json.dumps(j), s))

# csv = open('t.csv', 'a')
# for key, value in s[0].iteritems():
#     csv.write(key + ", ")
#
# for d in s:
#     csv.write("\n")
#     for key, value in d.iteritems():
#         csv.write(str(value) + ", ", )
# csv.close()
#
# print "Timed out requests count: " + str(len(fail))
# for f in fail:
#     print f


print
print(time.time() - start)
