#!/usr/bin/env python
import sys
from flask import Flask, request

app = Flask(__name__)
@app.route('/result', methods=['POST'])

def result():
    print("server" +  request.form['foo']) # should display 'bar'
    return 'Received !' # response to your request.

print "Content-type: text/html\n\n"
print "Hello UsainBolt"
app.run(host="192.168.0.1", port=80, debug=True)
EOF
