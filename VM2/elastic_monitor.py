from flask import Flask, jsonify, request, render_template
import sys
import pycurl
import json
import subprocess
from threading import Thread
import time
import random
import string
## probably needs alteration
light_ip_proxy = 'http://10.140.17.127:5010'
medium_ip_proxy = 'http://10.140.17.127:5020'
heavy_ip_proxy = 'http://10.140.17.127:5030'

light_ip_proxy_no_port = '10.140.17.127'
medium_ip_proxy_no_port = '10.140.17.127'
heavy_ip_proxy_no_port = '10.140.17.127'

light_port = 15002
medium_port = 16002
heavy_port = 17002

resm_addr = 'http://10.140.17.126:3000'

cURL = pycurl.Curl()
app = Flask(__name__)

class Monitor:

    def __init__(self, ):

        # Flag for continual monitoring
        self.l_active = False
        self.m_active = False
        self.h_active = False

        # Thresholds
        self.l_l = 0
        self.l_u = 0
        self.m_l = 0
        self.m_u = 0
        self.h_l = 0
        self.h_u = 0

        # lower and upper sizes
        self.l_low = 0
        self.l_up = 0
        self.m_low = 0
        self.m_up = 0
        self.h_low = 0
        self.h_up = 0

        # Monitoring rates
        self.l_rate = 2
        self.m_rate = 2
        self.h_rate = 2

        # Monitoring Arrays
        self.l_vals = []
        self.m_vals = []
        self.h_vals = []

        # Monitoring threads
        self.l_task = None
        self.m_task = None
        self.h_task = None

        # Nodes
        self.l_nodes = []
        self.m_nodes = []
        self.h_nodes = []

    def signal(self, ):
        cURL.setopt(cURL.URL, resm_addr + '/get_update')
        cURL.perform()
        print(cURL.getinfo(cURL.RESPONSE_CODE))

    def rand_name(self, length=10):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def num_running_nodes(self, flag):
        count = 0

        if flag == 'Light':
            for node in self.l_nodes:
                if node['running']:
                    count += 1
            return count

        if flag == 'Medium':
            for node in self.m_nodes:
                if node['running']:
                    count += 1
            return count

        if flag == 'Heavy':
            for node in self.h_nodes:
                if node['running']:
                    count += 1
            return count

    def l_monitoring(self, ):
        while(self.l_active):
            time.sleep(self.l_rate)

            cURL.setopt(cURL.URL, light_ip_proxy + '/monitor_resources')
            buffer = bytearray()

            cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
            cURL.perform()

            print(cURL.getinfo(cURL.RESPONSE_CODE))

            if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
                res_dict = json.loads(buffer.decode())
                cpu_percent = res_dict['cpu_percent']
                memory_percent = res_dict['mem_percent']
                weight_val = cpu_percent*0.5 + memory_percent*0.5
                print('cpu percentage: ' + str(cpu_percent) + ' ' + 'memory percentage: ' + str(memory_percent))
                print('weighted value: ' + str(weight_val))
                self.l_vals.append(weight_val)
                if len(self.l_vals) > 5:
                    self.l_vals.remove(self.l_vals[0])
                    curr_avg = sum(self.l_vals)/len(self.l_vals)
                    # decision making

                    if self.num_running_nodes('Light') == 0:
                        if len(self.l_nodes) > 0:
                            print('launch new node')
                            launch('Light')
                        else:
                            print('create and launch new node')
                            name = self.rand_name()
                            cloud_register(name, 'Light')
                            launch('Light')
                        self.signal()

                    if len(self.l_nodes) < self.l_low:
                        print("Creating node")
                        name = self.rand_name()
                        cloud_register(name, 'Light')
                        self.signal()
                    elif len(self.l_nodes) > self.l_up:
                        print("Removing node")
                        remove_node('Light')
                        self.signal()
                    elif curr_avg > self.l_u:
                        for node in self.l_nodes:
                            if not node['running']:
                                print("Launch new node")
                                launch('Light')
                                self.signal()
                                break
                        if len(self.l_nodes) < self.l_up:
                            name = self.rand_name()
                            print("Creating and launching new node")
                            cloud_register(name, 'Light')
                            launch('Light')
                            self.signal()
                    elif curr_avg < self.l_l:
                        if len(self.l_nodes) > self.l_low:
                            remove_node('Light')
                            self.signal()

    def m_monitoring(self, ):

        while(self.m_active):
            time.sleep(self.m_rate)

            cURL.setopt(cURL.URL, medium_ip_proxy + '/monitor_resources')
            buffer = bytearray()

            cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
            cURL.perform()

            print(cURL.getinfo(cURL.RESPONSE_CODE))

            if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
                res_dict = json.loads(buffer.decode())
                cpu_percent = res_dict['cpu_percent']
                memory_percent = res_dict['mem_percent']
                weight_val = cpu_percent*0.5 + memory_percent*0.5
                print('cpu percentage: ' + str(cpu_percent) + ' ' + 'memory percentage: ' + str(memory_percent))
                print('weighted value: ' + str(weight_val))
                self.m_vals.append(weight_val)
                if len(self.m_vals) > 5:
                    self.m_vals.remove(self.m_vals[0])
                    curr_avg = sum(self.m_vals)/len(self.m_vals)
                    # decision making
                    if self.num_running_nodes('Medium') == 0:
                        if len(self.m_nodes) > 0:
                            print('launch new node')
                            launch('Medium')
                        else:
                            print('create and launch new node')
                            name = self.rand_name()
                            cloud_register(name, 'Medium')
                            launch('Medium')
                        self.signal()

                    if len(self.m_nodes) < self.m_low:
                        print("Creating node")
                        name = self.rand_name()
                        cloud_register(name, 'Medium')
                        self.signal()
                    elif len(self.m_nodes) > self.m_up:
                        print("Removing node")
                        remove_node('Medium')
                        self.signal()
                    elif curr_avg > self.m_u:
                        for node in self.m_nodes:
                            if not node['running']:
                                print("Launch new node")
                                launch('Medium')
                                break
                        if len(self.m_nodes) < self.m_up:
                            name = self.rand_name()
                            print("Creating and launching new node")
                            cloud_register(name, 'Medium')
                            launch('Medium')
                            self.signal()
                    elif curr_avg < self.m_l:
                        if len(self.m_nodes) > self.m_low:
                            remove_node('Medium')
                            self.signal()


    def h_monitoring(self, ):

        while(self.h_active):
            time.sleep(self.h_rate)

            cURL.setopt(cURL.URL, heavy_ip_proxy + '/monitor_resources')
            buffer = bytearray()

            cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
            cURL.perform()

            print(cURL.getinfo(cURL.RESPONSE_CODE))

            if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
                res_dict = json.loads(buffer.decode())
                cpu_percent = res_dict['cpu_percent']
                memory_percent = res_dict['mem_percent']
                weight_val = cpu_percent*0.5 + memory_percent*0.5
                print('cpu percentage: ' + str(cpu_percent) + ' ' + 'memory percentage: ' + str(memory_percent))
                print('weighted value: ' + str(weight_val))
                self.h_vals.append(weight_val)
                if len(self.h_vals) > 5:
                    self.h_vals.remove(self.h_vals[0])
                    curr_avg = sum(self.h_vals)/len(self.h_vals)
                    # decision making

                    if self.num_running_nodes('Heavy') == 0:
                        if len(self.h_nodes) > 0:
                            print('launch new node')
                            launch('Heavy')
                        else:
                            print('create and launch new node')
                            name = self.rand_name()
                            cloud_register(name, 'Heavy')
                            launch('Heavy')
                        self.signal()

                    if len(self.h_nodes) < self.h_low:
                        print("Creating node")
                        name = self.rand_name()
                        cloud_register(name, 'Heavy')
                        self.signal()
                    elif len(self.h_nodes) > self.h_up:
                        print("Removing node")
                        remove_node('Heavy')
                    elif curr_avg > self.h_u:
                        for node in self.h_nodes:
                            if not node['running']:
                                print("Launch new node")
                                launch('Heavy')
                                self.signal()
                                break
                        if len(self.h_nodes) < self.h_up:
                            name = self.rand_name()
                            print("Creating and launching new node")
                            cloud_register(name, 'Heavy')
                            launch('Heavy')
                            self.signal()
                    elif curr_avg < self.h_l:
                        if len(self.h_nodes) > self.h_low:
                            remove_node('Heavy')
                            self.signal()

monitor = Monitor()

# set lower
@app.route('/lower/<pod_id>/<value>')
def monitor_set_lower(pod_id, value):
    value = float(value)
    if pod_id == 'Light':
        monitor.l_l = value
        return jsonify({'response': 'success'})

    if pod_id == 'Medium':
        monitor.m_l = value
        return jsonify({'response': 'success'})

    if pod_id == 'Heavy':
        monitor.h_l = value
        return jsonify({'response': 'success'})

# set upper
@app.route('/upper/<pod_id>/<value>')
def monitor_set_upper(pod_id, value):
    value = float(value)
    if pod_id == 'Light':
        monitor.l_u = value
        return jsonify({'response': 'success'})

    if pod_id == 'Medium':
        monitor.m_u = value
        return jsonify({'response': 'success'})

    if pod_id == 'Heavy':
        monitor.h_u = value
        return jsonify({'response': 'success'})

# enable
@app.route('/enable/<pod_id>/<lower>/<upper>/<port>')
def monitor_enable(pod_id, lower, upper, port):

    global light_port
    global medium_port
    global heavy_port
    lower = int(lower)
    upper = int(upper)
    port = int(port)

    if pod_id == 'Light':
        light_port = port
        monitor.l_low = lower
        monitor.l_up = upper
        monitor.l_vals = []
        monitor.l_active = True

        cURL.setopt(cURL.URL, light_ip_proxy + '/current_node_stats')
        buffer = bytearray()

        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        res_dict = json.loads(buffer.decode())
        monitor.l_nodes = res_dict['nodes']

        task = Thread(target=monitor.l_monitoring)
        monitor.l_task = task
        task.start()
        return jsonify({'response' : 'Successfully launch elastic mode for light pod'})

    if pod_id == 'Medium':
        medium_port = port
        monitor.m_low = lower
        monitor.m_up = upper
        monitor.m_vals = []
        monitor.m_active = True

        cURL.setopt(cURL.URL, medium_ip_proxy + '/current_node_stats')
        buffer = bytearray()

        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        res_dict = json.loads(buffer.decode())
        monitor.l_nodes = res_dict['nodes']

        task = Thread(target=monitor.m_monitoring)
        monitor.m_task = task
        task.start()
        return jsonify({'response' : 'Successfully launch elastic mode for medium pod'})

    if pod_id == 'Heavy':
        heavy_port = port
        monitor.h_low = lower
        monitor.h_up = upper
        monitor.h_vals = []
        monitor.h_active = True

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/current_node_stats')
        buffer = bytearray()

        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        res_dict = json.loads(buffer.decode())
        monitor.l_nodes = res_dict['nodes']

        task = Thread(target=monitor.h_monitoring)
        monitor.h_task = task
        task.start()
        return jsonify({'response' : 'Successfully launch elastic mode for heavy pod'})

# disable
@app.route('/disable/<pod_id>')
def monitor_disable(pod_id):

    if pod_id == 'Light':
        monitor.l_active = False
        monitor.l_task = None
        monitor.signal()
        return jsonify({'response': 'Elastic mode off for light pod'})

    if pod_id == 'Medium':
        monitor.m_active = False
        monitor.m_task = None
        monitor.signal()
        return jsonify({'response': 'Elastic mode off for medium pod'})

    if pod_id == 'Heavy':
        monitor.h_active = False
        monitor.h_task = None
        monitor.signal()
        return jsonify({'response': 'Elastic mode off for heavy pod'})

#---------------------------cloud register <node_name> <pod_name>--------
def cloud_register(node_name, pod_id):

    if pod_id == "Light":

        global light_port
        cURL.setopt(cURL.URL,light_ip_proxy + '/register/' + node_name + '/' + str(light_port))
        light_port +=  1

        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            reason = response_dictionary['reason']
            if response == 'success':
                name = response_dictionary['name']
                status = response_dictionary['running']
                port = response_dictionary['port']
                monitor.l_nodes.append({'name': name, 'running': status, 'port': port})

    if pod_id == "Medium":

        global medium_port
        cURL.setopt(cURL.URL, medium_ip_proxy + '/register/' + node_name + '/' + str(medium_port))
        medium_port += 1

        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            reason = response_dictionary['reason']
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                monitor.m_nodes.append({'name': name, 'running': running, 'port': port})

    if pod_id == "Heavy":

        global heavy_port
        cURL.setopt(cURL.URL, heavy_ip_proxy + '/register/' + node_name + '/' + str(heavy_port))
        heavy_port += 1

        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            reason = response_dictionary['reason']
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                monitor.h_nodes.append({'name': name, 'running': running, 'port': port})

#---------------------------cloud rm <name> <pod_id>---------------
def remove_node(pod_id):

    ## remove nodes in the light pod
    if pod_id == 'Light':

        if monitor.num_running_nodes('Light') in [0, 1]:
            print('No node to delete')
            return

        node_to_del = None
        for node in monitor.l_nodes:
            if node['running']:
                node_to_del = node
                break
        if node_to_del is None:
            print('No node to delete')
            return
        name = node_to_del['name']

        cURL.setopt(cURL.URL,light_ip_proxy + '/elastic/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        node_to_del['running'] = False

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
        disable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(disable_command, shell = True, check = True)
        command = "echo 'experimental-mode on; del server light-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(command, shell=True, check=True)

    ## removing the node from medium pod
    if pod_id == 'Medium':

        if monitor.num_running_nodes('Medium') in [0, 1]:
            print('No Node to delete')
            return

        node_to_del = None
        for node in monitor.m_nodes:
            if node['running']:
                node_to_del = node
                break

        if node_to_del is None:
            print('No node to delete')
            return
        name = node_to_del['name']

        cURL.setopt(cURL.URL, medium_ip_proxy + '/elastic/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        node_to_del['running'] = False

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
        disable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(disable_command, shell = True, check = True)
        command = "echo 'experimental-mode on; del server Medium-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(command, shell=True, check=True)

    ## removing the node from heavy pod
    if pod_id == 'Heavy':

        if monitor.num_running_nodes('Heavy') in [0, 1]:
            print('NO node to remove')
            return

        node_to_del = None
        for node in monitor.h_nodes:
            if node['running']:
                node_to_del = node
                break

        if node_to_del is None:
            print('No node to delete')
            return

        name = node_to_del['name']

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/elastic/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        node_to_del['running'] = False

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
        disable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(disable_command, shell = True, check = True)
        command = "echo 'experimental-mode on; del server heavy-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
        subprocess.run(command, shell=True, check=True)

#---------------------------cloud launch <pod_id>---------------
def launch(pod_id):

    if pod_id == 'Light':

        cURL.setopt(cURL.URL, light_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in monitor.l_nodes:
                    if node['name'] == name:
                        node['running'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server light-servers/'" + name + ' ' + light_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)

    if pod_id == 'Medium':

        cURL.setopt(cURL.URL, medium_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in monitor.m_nodes:
                    if node['name'] == name:
                        node['running'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server Medium-servers/'" + name + ' ' + medium_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)

    if pod_id == 'Heavy':

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in monitor.h_nodes:
                    if node['name'] == name:
                        node['running'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server heavy-servers/'" + name + ' ' + heavy_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)


@app.route('/update_resm')
def return_update():
    l_nodes = monitor.l_nodes
    m_nodes = monitor.m_nodes
    h_nodes = monitor.h_nodes

    resl = []
    for node in l_nodes:
        resl.append({'name': node['name'], 'status': node['running']})

    resm = []
    for node in m_nodes:
        resm.append({'name': node['name'], 'status': node['running']})

    resh = []
    for node in h_nodes:
        resh.append({'name': node['name'], 'status': node['running']})

    return jsonify({'l_nodes': resl, 'm_nodes': resm, 'h_nodes': resh, 'lp': light_port, 'mp': medium_port, 'hp': heavy_port})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3010)