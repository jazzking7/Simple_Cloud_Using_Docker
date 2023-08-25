from flask import Flask, render_template, jsonify, request
from datetime import datetime
import pycurl
import json
import sys

cURL = pycurl.Curl()
app = Flask(__name__)

pending_requests = []
processed_requests = []

l_url = "http://10.140.17.126:5010"
m_url = "http://10.140.17.126:5020"
h_url = "http://10.140.17.126:5030"

@app.route('/render_requests')
def render_page():
    return render_template('request_monitor.html',
            pending_requests = pending_requests,
            processed_requests = processed_requests)

@app.route('/Light')
def launch_light():
    try:
        now = datetime.now()
        pending_requests.append({"type": "Light", "time": now})
        render_page()
        cURL.setopt(cURL.URL, l_url)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            res_dict = json.loads(buffer.decode())
            processed_requests.append({"type": "Light", "time": now, "log": res_dict["response"]})
            render_page()
            return res_dict["response"] + "\n"
        else:
            return "Error while processing the request"
    except:
        return "server connection error, Light pod not available"

@app.route('/Medium')
def launch_medium():
    try:
        now = datetime.now()
        pending_requests.append({"type": "Medium", "time": now})
        render_page()

        cURL.setopt(cURL.URL, m_url)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            res_dict = json.loads(buffer.decode())
            processed_requests.append({"type": "Medium", "time": now, "log": res_dict["response"]})
            render_page()
            return res_dict["response"] + "\n"
        else:
            return "Error while processing the request"
    except:
        return "server connection error, Medium pod not available"


@app.route('/Heavy')
def launch_heavy():
    try:
        now = datetime.now()
        pending_requests.append({"type": "Heavy", "time": now})
        render_page()

        cURL.setopt(cURL.URL, h_url)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            res_dict = json.loads(buffer.decode())
            processed_requests.append({"type": "Heavy", "time": now, "log": res_dict["response"]})
            render_page()
            return res_dict["response"] + "\n"
        else:
            return "Error while processing the request"
    except:
        return "server connection error, Light pod not available"

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7000)