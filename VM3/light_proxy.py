from flask import Flask, jsonify, request
import sys
import docker

client = docker.from_env()
app = Flask(__name__)

## proxy takes care of launching, we need a node list to know which node is available
node_list = []
maximum = 20

# Pausing
class Pausing:
    def __init__(self,):
        self.Available = True
        return
P = Pausing()

# checked
@app.route('/init')
def cloud_init():
    [img, logs] = client.images.build(path='/home/comp598-user/', rm = True, dockerfile='/home/comp598-user/Dockerfile.light')
    node_name = 'default_1'
    port = '15001'
    running = False
    client.containers.create(image= img,
                          detach=True,
                          name='Light_'+node_name,
                          ports = {'5010/tcp':'15001'},
                          cpu_percent= 30,
                          mem_limit= '100m')
    node_list.append({'port':port, 'name':node_name, 'running': False})
    return jsonify({'response': 'success',
                        'port': port,
                        'name': node_name,
                        'running': False,
                        'node_list': node_list})

##---------------------------cloud register <node_name>--------------
# checked
@app.route('/register/<node_name>/<port>')
def cloud_register(node_name, port):
    if len(node_list) == 20:
        return jsonify({'response': 'register node files',
            'reason': 'the Light pod can take maximum 20 nodes'})
    for node in node_list:
        if node['port'] == port:
            return jsonify({'response': 'failure',
                            'reason': ' port already taken'})
        elif node['name'] == node_name:
            return jsonify({'response': 'failure',
                            'reason': 'name already taken'})
    [img, logs] = client.images.build(path='/home/comp598-user/', rm = True, dockerfile='/home/comp598-user/Dockerfile.light')
    client.containers.create(image= img,
                          detach=True,
                          name=str('Light_'+node_name),
                          ports = {'5010/tcp':str(port)},
                          cpu_percent= 30,
                          mem_limit= '100m')
    node_list.append({'port':port, 'name':node_name, 'running': False})
    return jsonify({'response': 'success',
                        'port': port,
                        'name': node_name,
                        'running': False,
                        'node_list': node_list,
                        'reason': 'successful'})


##---------------cloud rm <node_name> <pod_name> ------------
# checked
@app.route('/cloud/rm/<node_name>')
def cloud_rm(node_name):
    index_to_remove = -1
    for i in range(len(node_list)):
        node = node_list[i]
        if node['name'] == node_name:
            index_to_remove = i
            break
    found = False
    port = -1
    name = ''
    running = False
    if index_to_remove != -1:
        node = node_list[index_to_remove]
        port = node['port']
        name = node['name']
        running = node['running']
        del node_list[index_to_remove]
        found = True

    for container in client.containers.list(all=True):
        if container.name == str('Light_'+node_name):
            container.remove(v=True, force=True)
            break

    if found:
        return jsonify({'response': 'success',
                        'port': port,
                        'name': name,
                        'running': running,
                        'node_list':node_list})
    return jsonify({'response': 'failure',
        'reason': 'could not find the node in the pod'})

##-------------------cloud launch------------------------------------
# checked
@app.route('/launch')
def launch():
    # Pausing
    if not P.Available:
        return jsonify({'response': 'PodPaused'})
    ## loop through the node_list and find the first node that is not running
    for node in node_list:
        if not node['running']:
            node = launch_node(node['name'], node['port'])
            if node is not None:
                return jsonify({'response': 'success',
                    'port': node['port'],
                    'name':str(node['name']),
                    'running': node['running']})
    return jsonify({'response': 'failure'})

# launch helper
def launch_node(container_name, port_number):
    [img, logs] = client.images.build(path='/home/comp598-user', rm = True, dockerfile='/home/comp598-user/Dockerfile.light')
    for container in client.containers.list(all=True):
        if container.name == str('Light_'+container_name):
            container.remove(v=True, force= True)
            break
    client.containers.run(image= img,
                          detach=True,
                          name=str('Light_'+container_name),
                          command=['python3', 'l_job.py',str('Light_'+container_name) ],
                          ports = {'5010/tcp': port_number},
                          cpu_percent= 30,
                          mem_limit= '100m')

    index = -1
    for i in range(len(node_list)):
        node = node_list[i]
        if container_name == node['name']:
            index = i
            node_list[i] = {'port':port_number,
                            'name': container_name,
                            'running':True}
            break

    print('Successfully launched a node')
    return node_list[index]

##--------------------------cloud pause---------------------------
# checked
@app.route('/cloud/pause')
def cloud_pause():

    running_nodes = []
    for i in range(len(node_list)):
        node = node_list[i]
        if node['running']:
            running_nodes.append(node)
    # Pausing
    P.Available = False
    return jsonify({"response":'success',
            'running_nodes': running_nodes})


##---------------------------cloud resume---------------------------
# checked
@app.route('/cloud/resume')
def cloud_resume():
    P.Available = True
    running_nodes = []
    for node in node_list:
        if node['running']:
            running_nodes.append(node)
    return jsonify({"response": 'success', "running_nodes": running_nodes})

##--------------------------monitor resources-----------------------
@app.route('/monitor_resources')
def monitor_resources():
    cpu_usage = 0.0
    mem_usage = 0.0

    names = []
    light_containers = []

    for node in node_list:
        if node['running']:
            names.append('Light_' + node['name'])

    for container in client.containers.list(all=True):
        if container.name in names:
            light_containers.append(container)

    for container in light_containers:
        stats = container.stats(stream=False)

        cpu_stats = stats["cpu_stats"]
        previous_cpu_stats = stats["precpu_stats"]

        container_execution_time_delta = float(cpu_stats["cpu_usage"]["total_usage"]) - float(previous_cpu_stats["cpu_usage"]["total_usage"])
        total_container_time_delta = float(cpu_stats["system_cpu_usage"]) - float(previous_cpu_stats["system_cpu_usage"])
        cpu_usage += container_execution_time_delta / total_container_time_delta * 100.0

        memory_stats = stats['memory_stats']
        mem_usage += memory_stats['usage'] / memory_stats['limit'] * 100.0


    if len(light_containers) != 0:
        cpu_usage = cpu_usage/len(light_containers)
        mem_usage = mem_usage/len(light_containers)

    return jsonify({'cpu_percent' : cpu_usage, 'mem_percent': mem_usage})

##-----------------------------current stats---------------------------
@app.route('/current_node_stats')
def current_node_stats():
    return jsonify({'nodes': node_list})


##------------------------------elastic remove-------------------------
@app.route('/elastic/rm/<name>')
def elastic_remove(name):

    for i in range(len(node_list)):
        node = node_list[i]
        if node['name'] == name:
            node['running'] = False
            break

    for container in client.containers.list(all=True):
        if container.name == str('Light_'+name):
            container.stop()
            container.remove()
            break
    return jsonify({'response': 'successful removal'})

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port=5010)