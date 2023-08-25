import pycurl
import sys
import os
import requests
import time
import math as m
import random

cURL = pycurl.Curl()
lb_url = "http://10.140.17.126:7000"

l_res_times = []
m_res_times = []
h_res_times = []

def launch_light(url):
    try:
        cURL.setopt(cURL.URL, url + "/Light")
        start = time.time()
        cURL.perform()
        end = time.time()
        l_res_times.append(end - start)
        print("Took the light server " + str(end - start) + " seconds to respond\n")
    except:
        print('server connection error, Light pod not available')

def launch_medium(url):
    try:
        cURL.setopt(cURL.URL, url + "/Medium")
        start = time.time()
        cURL.perform()
        end = time.time()
        m_res_times.append(end - start)
        print("Took the medium server " + str(end - start) + " seconds to respond\n")

    except:
        print('server connection error, Medium pod not available')

def launch_heavy(url):
    try:
        cURL.setopt(cURL.URL, url + "/Heavy")
        start = time.time()
        cURL.perform()
        end = time.time()
        h_res_times.append(end - start)
        print("Took the heavy server " + str(end - start) + " seconds to respond\n")
    except:
        print('server connection error, Heavy pod not available')

def launch_light_auto(url, dur, intval, amt, irr):
    num_peaks = m.ceil(dur/intval)
    for i in range(num_peaks):
        cur_amt = amt
        if irr:
            cur_amt = random.randint(1, amt)
        for j in range(cur_amt):
            try:
                cURL.setopt(cURL.URL, url + "/Light")
                cURL.perform()
            except:
                print('server connection error, Light pod not available')
        time.sleep(intval)

def launch_medium_auto(url, dur, intval, amt, irr):
    num_peaks = m.ceil(dur/intval)
    for i in range(num_peaks):
        cur_amt = amt
        if irr:
            cur_amt = random.randint(1, amt)
        for j in range(cur_amt):
            try:
                cURL.setopt(cURL.URL, url + "/Medium")
                cURL.perform()
            except:
                print('server connection error, Medium pod not available')
        time.sleep(intval)

def launch_heavy_auto(url, dur, intval, amt, irr):
    num_peaks = m.ceil(dur/intval)
    for i in range(num_peaks):
        cur_amt = amt
        if irr:
            cur_amt = random.randint(1, amt)
        for j in range(cur_amt):
            try:
                cURL.setopt(cURL.URL, url + "/Heavy")
                cURL.perform()
            except:
                print('server connection error, Heavy pod not available')
        time.sleep(intval)

def main():
    while(1):
        option = input('[1] -> Manual Mode  [2] -> Auto Mode  [3] -> Quit: ')
        if option == '1':
            while(1):
                command = input('[1] -> Light  [2] -> Medium  [3] -> Heavy  [4] -> Quit: ')
                if command == '1':
                    launch_light(lb_url)
                elif command == '2':
                    launch_medium(lb_url)
                elif command == '3':
                    launch_heavy(lb_url)
                elif command == '4':
                    break
        elif option == '2':
            while(1):
                command = input('[1] -> Light  [2] -> Medium  [3] -> Heavy  [4] -> Quit: ')
                if command == '4':
                    break
                duration = int(input('Enter duration (s): '))
                interval = int(input('Enter interval (s): '))
                amount = int(input('Enter amount: '))
                irregular = bool(input('Irregularity (0/1): '))
                if command == '1':
                    launch_light_auto(lb_url, duration, interval, amount, irregular)
                elif command == '2':
                    launch_medium_auto(lb_url, duration, interval, amount, irregular)
                elif command == '3':
                    launch_heavy_auto(lb_url, duration, interval, amount, irregular)
        elif option == '3':
            break

if __name__ == '__main__':
    main()