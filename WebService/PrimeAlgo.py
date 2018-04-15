#!/usr/bin/env python
import time
import math

def closestPrime(num):
    for i in range(num, 1, -1):
        isPrime = True
        for j in range(2,int(math.ceil(math.sqrt(i)))):
            if i % j == 0:
                isPrime = False
            if isPrime:
                return i

start = time.clock()
print closestPrime(123456)
print time.clock() - start
