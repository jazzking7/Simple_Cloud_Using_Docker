import time
from flask import Flask, jsonify
import sys

app = Flask(__name__)

@app.route('/')
def fast_print():
    if len(sys.argv) < 2:
        return jsonify({"response", "Something went wrong"})
    start_time = time.time()
    for i in range(10):
        print("Hello " + str(i))
    end_time = time.time()
    message = "From: " + sys.argv[1] + "\n"
    res = message + "Execution time: " + str(start_time - end_time) +  " seconds"
    return jsonify({"response": res})

if __name__ == '__main__':
    app.run(debug = True, host='0.0.0.0', port=5010)