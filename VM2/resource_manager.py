from flask import Flask, jsonify, request, render_template
import sys
import pycurl
import json
import subprocess

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

cURL = pycurl.Curl()
app = Flask(__name__)

# For Dashboard Display
# Nodename, State
l_nodes = []
m_nodes = []
h_nodes = []

# Status
l_pod = [True]
m_pod = [True]
h_pod = [True]

# Auto_Flag
L_A = False
M_A = False
H_A = False

# Elastis Monitor Location
elastic_proxy = 'http://10.140.17.126:3010'

# Render Function
@app.route('/render')
def render_page():
    return render_template('index.html',
            l_nodes = l_nodes, l_pod = l_pod,
            m_nodes = m_nodes, m_pod = m_pod,
            h_nodes = h_nodes, h_pod = h_pod)

##---------------------------cloud init------------------------------------
@app.route('/init')
def cloud_init():

    ## initialize the light pod
    cURL.setopt(cURL.URL,light_ip_proxy + '/init')
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        light_response_dictionary = json.loads(buffer.decode())
        light_response = light_response_dictionary['response']
        if light_response == 'success':
            node_name = light_response_dictionary['name']
            node_status = light_response_dictionary['running']
            l_nodes.append({'name': node_name, 'status': node_status})
            print("Light Pod Successfully Activated")
        else:
            return jsonify({'response': 'failure',
                    'reason': 'Light pod initalization failed'})

    ## initialize the medium pod
    cURL.setopt(cURL.URL,medium_ip_proxy + '/init')
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        medium_response_dictionary = json.loads(buffer.decode())
        medium_response = medium_response_dictionary['response']
        if medium_response == 'success':
            node_name = medium_response_dictionary['name']
            node_status = medium_response_dictionary['running']
            m_nodes.append({'name': node_name, 'status': node_status})
            print("Medium Pod Successfully Activated")
        else:
            return jsonify({'response': 'failure',
                    'reason': 'Medium pod initalization failed'})

    ## initialize the heavy pod
    cURL.setopt(cURL.URL,heavy_ip_proxy + '/init')
    buffer = bytearray()

    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        heavy_response_dictionary = json.loads(buffer.decode())
        heavy_response = heavy_response_dictionary['response']
        if heavy_response == 'success':
            node_name = heavy_response_dictionary['name']
            node_status = heavy_response_dictionary['running']
            h_nodes.append({'name': node_name, 'status': node_status})
            print("Heavy Pod Successfully Activated")
        else:
            return jsonify({'response': 'failure',
                    'reason': 'Heavy pod initalization failed'})
    render_page()
    return jsonify({'response': 'Successfully initiated the three proxies'})

##--------------------------cloud pod register---------------------------
# checked
@app.route('/cloud/pod/register/<pod_name>')
def cloud_pod_register(pod_name):
    return jsonify({'response': 'The current cloud system cannot register new pods'})


##--------------------------cloud pod rm---------------------------------
# checked
@app.route('/cloud/pod/rm/<pod_name>')
def cloud_pod_rm(pod_name):
     return jsonify({'response': 'The current cloud system does not allow users to remove pods'})

#---------------------------cloud register <node_name> <pod_name>--------
# checked
@app.route('/cloud/register/<node_name>/<pod_id>')
def cloud_register(node_name, pod_id):

    if pod_id not in ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'fail to register the node',
            'reason': 'pod_id need to be Light, Medium, or Heavy'})

    if pod_id == 'Light' and L_A:
        return jsonify({'response': 'fail to register the node',
            'reason': 'Elastic Monitoring on for light pod'})

    if pod_id == 'Medium' and M_A:
        return jsonify({'response': 'fail to register the node',
            'reason': 'Elastic Monitoring on for medium pod'})

    if pod_id == 'Heavy' and H_A:
        return jsonify({'response': 'fail to register the node',
            'reason': 'Elastic Monitoring on for heavy pod'})

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
                node_list = response_dictionary['node_list']
                l_nodes.append({'name': name, 'status': status})
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': status,
                            'node_list': node_list})
            else:
                render_page()
                return jsonify({'response': 'failed',
                'reason': reason})

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
                node_list = response_dictionary['node_list']
                m_nodes.append({'name': name, 'status': running})
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running,
                            'node_list': node_list})
            else:
                render_page()
                return jsonify({'response': 'failed',
                'reason': reason})

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
                node_list = response_dictionary['node_list']
                h_nodes.append({'name': name, 'status': running})
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running,
                            'node_list': node_list})
            else:
                render_page()
                return jsonify({'response': 'failed',
                'reason': reason})

    return jsonify({'response': 'failed',
                'reason': 'unknown'})

#---------------------------cloud rm <name> <pod_id>---------------
# checked
@app.route('/cloud/rm/<name>/<pod_id>')
def remove_node(name, pod_id):

    if pod_id not in ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    if pod_id == 'Light' and L_A:
        return jsonify({'response': 'fail to remove the node',
            'reason': 'Elastic Monitoring on for light pod'})

    if pod_id == 'Medium' and M_A:
        return jsonify({'response': 'fail to remove the node',
            'reason': 'Elastic Monitoring on for medium pod'})

    if pod_id == 'Heavy' and H_A:
        return jsonify({'response': 'fail to remove the node',
            'reason': 'Elastic Monitoring on for heavy pod'})

    ## remove nodes in the light pod
    if pod_id == 'Light':

        cURL.setopt(cURL.URL,light_ip_proxy + '/cloud/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        print(cURL.getinfo(cURL.RESPONSE_CODE))
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'failure':
                return jsonify({'response': 'failure', 'reason': response_dictionary['reason']})
            elif response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                node_list = response_dictionary['node_list']
                # removed from webpage display
                index = -1
                for i in range(len(l_nodes)):
                    if l_nodes[i]['name'] == name:
                        index = i
                        break
                del l_nodes[index]
                if running:
                    disable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server light-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running,
                            'node_list': node_list})

    ## removing the node from medium pod
    if pod_id == 'Medium':

        cURL.setopt(cURL.URL, medium_ip_proxy + '/cloud/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        print(cURL.getinfo(cURL.RESPONSE_CODE))
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'failure':
                return jsonify({'response': 'failure', 'reason': response_dictionary['reason']})
            elif response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                node_list = response_dictionary['node_list']
                # removed from webpage display
                index = -1
                for i in range(len(m_nodes)):
                    if m_nodes[i]['name'] == name:
                        index = i
                        break
                del m_nodes[index]
                if running:
                    disable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server Medium-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running,
                            'node_list': node_list})

    ## removing the node from heavy pod
    if pod_id == 'Heavy':

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/cloud/rm/' + name)
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        print(cURL.getinfo(cURL.RESPONSE_CODE))
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'failure':
                return jsonify({'response': 'failure', 'reason': response_dictionary['reason']})
            elif response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                node_list = response_dictionary['node_list']
                # removed from webpage display
                index = -1
                for i in range(len(h_nodes)):
                    if h_nodes[i]['name'] == name:
                        index = i
                        break
                del h_nodes[index]
                if running:
                    disable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server heavy-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                render_page()
                return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running,
                            'node_list': node_list})

    return jsonify({'response': 'failure','reason': 'unknown'})

#---------------------------cloud launch <pod_id>---------------
# checked
@app.route('/cloud/launch/<pod_id>')
def launch(pod_id):

    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    if pod_id == 'Light' and L_A:
        return jsonify({'response': 'fail to launch the node',
            'reason': 'Elastic Monitoring on for light pod'})

    if pod_id == 'Medium' and M_A:
        return jsonify({'response': 'fail to launch the node',
            'reason': 'Elastic Monitoring on for medium pod'})

    if pod_id == 'Heavy' and H_A:
        return jsonify({'response': 'fail to launch the node',
            'reason': 'Elastic Monitoring on for heavy pod'})

    if pod_id == 'Light':

        cURL.setopt(cURL.URL, light_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'PodPaused':
                return jsonify({'response': 'failure',
                    'reason': 'Pod Paused'})
            elif response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in l_nodes:
                    if node['name'] == name:
                        node['status'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server light-servers/'" + name + ' ' + light_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                    render_page()
                    return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running})

    if pod_id == 'Medium':

        cURL.setopt(cURL.URL, medium_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'PodPaused':
                return jsonify({'response': 'failure',
                    'reason': 'Pod Paused'})
            elif response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in m_nodes:
                    if node['name'] == name:
                        node['status'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server Medium-servers/'" + name + ' ' + medium_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                    render_page()
                    return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running})

    if pod_id == 'Heavy':

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/launch')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'PodPaused':
                return jsonify({'response': 'failure',
                    'reason': 'Pod Paused'})
            if response == 'success':
                port = response_dictionary['port']
                name = response_dictionary['name']
                running = response_dictionary['running']
                for node in h_nodes:
                    if node['name'] == name:
                        node['status'] = running
                        break
                if running:
                    command = "echo 'experimental-mode on; add server heavy-servers/'" + name + ' ' + heavy_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                    render_page()
                    return jsonify({'response': 'success',
                            'port': port,
                            'name': name,
                            'running': running})

    return jsonify({'response': 'failure',
                    'reason': 'unknown'})

##---------------------------------cloud pause <pod_id>------------------
# checked
@app.route('/cloud/pause/<pod_id>')
def cloud_pause(pod_id):

    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    if pod_id == 'Light' and L_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring on for light pod'})

    if pod_id == 'Medium' and M_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring on for medium pod'})

    if pod_id == 'Heavy' and H_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring on for heavy pod'})

    if pod_id == 'Light':

        cURL.setopt(cURL.URL, light_ip_proxy + '/cloud/pause')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                running_nodes =  response_dictionary['running_nodes']
                print(running_nodes)
                for node in running_nodes:
                    port = node['port']
                    name = node['name']
                    disable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server light-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                disable_front = "echo 'experimental-mode on; disable frontend light' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(disable_front, shell=True, check=True)
                l_pod[0] = False
                for node in l_nodes:
                    node['status'] = False
                render_page()
                return jsonify({'response': 'successful'})
            return jsonify({'response': 'failure',
                    'reason': 'unknown'})

    if pod_id == 'Medium':

        cURL.setopt(cURL.URL, medium_ip_proxy + '/cloud/pause')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                running_nodes =  response_dictionary['running_nodes']
                print(running_nodes)
                for node in running_nodes:
                    port = node['port']
                    name = node['name']
                    disable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server Medium-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                disable_front = "echo 'experimental-mode on; disable frontend medium' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(disable_front, shell=True, check=True)
                m_pod[0] = False
                for node in m_nodes:
                    node['status'] = False
                render_page()
                return jsonify({'response': 'successful'})
            return jsonify({'response': 'failure',
                    'reason': 'unknown'})

    if pod_id == 'Heavy':

        cURL.setopt(cURL.URL, heavy_ip_proxy + '/cloud/pause')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()

        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                running_nodes =  response_dictionary['running_nodes']
                print(running_nodes)
                for node in running_nodes:
                    port = node['port']
                    name = node['name']
                    disable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state maint '+ '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(disable_command, shell = True, check = True)
                    command = "echo 'experimental-mode on; del server heavy-servers/'" + name + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check=True)
                disable_front = "echo 'experimental-mode on; disable frontend heavy' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(disable_front, shell=True, check=True)
                h_pod[0] = False
                for node in h_nodes:
                    node['status'] = False
                render_page()
                return jsonify({'response': 'successful'})
            return jsonify({'response': 'failure',
                    'reason': 'unknown'})

    return  jsonify({'response': 'fail to pause the pods'})

##---------------------------------------cloud resume--------------------------------------------------------

@app.route('/cloud/resume/<pod_id>')
# checked
def cloud_resume(pod_id):

    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    if pod_id == 'Light':
        cURL.setopt(cURL.URL, light_ip_proxy + '/cloud/resume')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                enable_front = "echo 'experimental-mode on; enable frontend light' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(enable_front, shell=True, check=True)
                rnodes = response_dictionary["running_nodes"]
                rnames = []
                for node in rnodes:
                    port = node['port']
                    name = node['name']
                    rnames.append(name)
                    command = "echo 'experimental-mode on; add server light-servers/'" + name + ' ' + light_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server light-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                l_pod[0] = True
                for n in l_nodes:
                    if n['name'] in rnames:
                        n['status'] = True
                render_page()
                return jsonify({'response': 'successful'})

    if pod_id == 'Medium':
        cURL.setopt(cURL.URL, medium_ip_proxy + '/cloud/resume')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                enable_front = "echo 'experimental-mode on; enable frontend medium' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(enable_front, shell=True, check=True)
                rnodes = response_dictionary["running_nodes"]
                rnames = []
                for node in rnodes:
                    port = node['port']
                    name = node['name']
                    rnames.append(name)
                    command = "echo 'experimental-mode on; add server Medium-servers/'" + name + ' ' + medium_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server Medium-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                m_pod[0] = True
                for n in m_nodes:
                    if n['name'] in rnames:
                        n['status'] = True
                render_page()
                return jsonify({'response': 'successful'})

    if pod_id == 'Heavy':
        cURL.setopt(cURL.URL, heavy_ip_proxy + '/cloud/resume')
        buffer = bytearray()
        cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
        cURL.perform()
        if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
            response_dictionary = json.loads(buffer.decode())
            response = response_dictionary['response']
            if response == 'success':
                enable_front = "echo 'experimental-mode on; enable frontend heavy' " + '| sudo socat stdio /var/run/haproxy.sock'
                subprocess.run(enable_front, shell=True, check=True)
                rnodes = response_dictionary["running_nodes"]
                rnames = []
                for node in rnodes:
                    port = node['port']
                    name = node['name']
                    rnames.append(name)
                    command = "echo 'experimental-mode on; add server heavy-servers/'" + name + ' ' + heavy_ip_proxy_no_port + ':' + port + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(command, shell=True, check = True)
                    enable_command = "echo 'experimental-mode on; set server heavy-servers/'" + name + ' state ready ' + '| sudo socat stdio /var/run/haproxy.sock'
                    subprocess.run(enable_command, shell=True, check=True)
                h_pod[0] = True
                for n in h_nodes:
                    if n['name'] in rnames:
                        n['status'] = True
                render_page()
                return jsonify({'response': 'successful'})


@app.route('/cloud/lower/<pod_id>/<value>')
def cloud_elasticity_lower_threshold(pod_id, value):
    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
            'reason': 'pod id should be Light, Medium, or Heavy'})

    cURL.setopt(cURL.URL, elastic_proxy + '/lower/' + pod_id + '/' + str(value))
    buffer = bytearray()
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        res_dict = json.loads(buffer.decode())
        return jsonify(res_dict)
    return jsonify({'response': 'failure'})

@app.route('/cloud/upper/<pod_id>/<value>')
def cloud_elasticity_upper_threshold(pod_id, value):
    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    cURL.setopt(cURL.URL, elastic_proxy + '/upper/' + pod_id + '/' + str(value))
    buffer = bytearray()
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        res_dict = json.loads(buffer.decode())
        return jsonify(res_dict)
    return jsonify({'response': 'failure'})

@app.route('/cloud/elastic/enable/<pod_id>/<lower_size>/<upper_size>')
def cloud_elasticity_enable(pod_id, lower_size, upper_size):
    global L_A
    global M_A
    global H_A
    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})

    if pod_id == 'Light' and L_A:
        return jsonify({'response': 'fail to enable',
            'reason': 'Elastic Monitoring on for light pod'})

    if pod_id == 'Medium' and M_A:
        return jsonify({'response': 'fail to enable',
            'reason': 'Elastic Monitoring on for medium pod'})

    if pod_id == 'Heavy' and H_A:
        return jsonify({'response': 'fail to enable',
            'reason': 'Elastic Monitoring on for heavy pod'})

    port = 0
    if pod_id == 'Light':
        port = light_port
    elif pod_id == 'Medium':
        port = medium_port
    elif pod_id == 'Heavy':
        port = heavy_port

    cURL.setopt(cURL.URL, elastic_proxy + '/enable/' + pod_id + '/' + str(lower_size) + '/' + str(upper_size) + '/' + str(port))
    buffer = bytearray()
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        if pod_id == 'Light':
            L_A = True
        elif pod_id == 'Medium':
            M_A = True
        elif pod_id == 'Heavy':
            H_A = True
        res_dict = json.loads(buffer.decode())
        return jsonify(res_dict)
    return jsonify({'response': 'failure'})


@app.route('/cloud/elastic/disable/<pod_id>')
def cloud_elasticity_disable(pod_id):
    global L_A
    global M_A
    global H_A
    if pod_id not in  ['Light', 'Medium', 'Heavy']:
        return jsonify({'response': 'failure',
                    'reason': 'pod id should be Light, Medium, or Heavy'})
    if pod_id == 'Light' and not L_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring not on for light pod'})

    if pod_id == 'Medium' and not M_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring not on for medium pod'})

    if pod_id == 'Heavy' and not H_A:
        return jsonify({'response': 'fail to pause the pod',
            'reason': 'Elastic Monitoring not on for heavy pod'})

    cURL.setopt(cURL.URL, elastic_proxy + '/disable/' + pod_id)
    buffer = bytearray()
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    if cURL.getinfo(cURL.RESPONSE_CODE) == 200:
        if pod_id == 'Light':
            L_A = False
        elif pod_id == 'Medium':
            M_A = False
        elif pod_id == 'Heavy':
            H_A = False
        res_dict = json.loads(buffer.decode())
        return jsonify(res_dict)
    return jsonify({'response': 'failure'})

@app.route('/get_update')
def get_update():
    cURL.setopt(cURL.URL, elastic_proxy + '/update_resm')
    buffer = bytearray()
    cURL.setopt(cURL.WRITEFUNCTION, buffer.extend)
    cURL.perform()

    print(cURL.getinfo(cURL.RESPONSE_CODE))
    res_dict = json.loads(buffer.decode())

    global light_port
    global medium_port
    global heavy_port
    global l_nodes
    global m_nodes
    global h_nodes

    if light_port < res_dict['lp']:
        light_port = res_dict['lp']

    if medium_port < res_dict['mp']:
        medium_port = res_dict['mp']

    if heavy_port < res_dict['hp']:
        heavy_port = res_dict['hp']

    if L_A:
        l_nodes = res_dict['l_nodes']

    if M_A:
        m_nodes = res_dict['m_nodes']

    if H_A:
        h_nodes = res_dict['h_nodes']
    render_page()
    return "UPDATE INFORMATION"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)