import pycurl
import sys
import os
import requests

cURL = pycurl.Curl()

# checked
def cloud_init(url):
    cURL.setopt(cURL.URL, url + '/init')
    cURL.perform()
# checked
def cloud_pod_register(url):
    cURL.setopt(cURL.URL, url + 'cloud/pod/register/' + 'fail')
    cURL.perform()
# checked
def cloud_pod_rm(url, command):
    command_list = command.split()
    cURL.setopt(cURL.URL, url + '/cloud/pod/rm/' + 'fail' )
    cURL.perform()
# checked
def cloud_register(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/register/' + command_list[2] +'/' + command_list[3])
        cURL.perform()
    else:
        print('cloud register need to follow this format: cloud register <node_name> <pod_name>')
# checked
def cloud_rm(url, command):
    command_list = command.split()
    if len(command_list) ==4:
        cURL.setopt(cURL.URL, url + '/cloud/rm/' + command_list[2] +'/' + command_list[3])
        cURL.perform()
    else:
        print('cloud remove node need to follow the pattern: cloud rm <node_name> <pod_name>')
# checked
def cloud_launch(url,command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/launch/' + command_list[2] )
        cURL.perform()
    else:
        print('cloud launch need to be specify the pod name')
# checked
def cloud_resume(url,command):
    command_list = command.split()
    if len(command_list) ==3:
        cURL.setopt(cURL.URL, url + '/cloud/resume/'  + command_list[2] )
        cURL.perform()
    else:
        print('cloud resume need to specify the pod name')
# checked
def cloud_pause(url, command):
    command_list = command.split()
    if len(command_list) ==3:
        cURL.setopt(cURL.URL, url + '/cloud/pause/' + command_list[2] )
        cURL.perform()
    else:
        print('cloud pause need to specify the pod name')

def cloud_set_lower(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/lower/' + command_list[2] + '/' + command_list[3])
        cURL.perform()
    else:
        print('Usage: cloud lower <pod_id> <value>')

def cloud_set_upper(url, command):
    command_list = command.split()
    if len(command_list) == 4:
        cURL.setopt(cURL.URL, url + '/cloud/upper/' + command_list[2] + '/' + command_list[3])
        cURL.perform()
    else:
        print('Usage: cloud upper <pod_id> <value>')

def cloud_enable_elastic(url, command):
    command_list = command.split()
    if len(command_list) == 5:
        if int(command_list[3]) >= int(command_list[4]):
            print('Lower size cannot be greater than upper size!')
            return
        cURL.setopt(cURL.URL, url + '/cloud/elastic/enable/' + command_list[2] + '/' + command_list[3] + '/' + command_list[4])
        cURL.perform()
    else:
        print('Usage: cloud enable <pod_id> <lower_size> <upper_size>')

def cloud_disable_elastic(url, command):
    command_list = command.split()
    if len(command_list) == 3:
        cURL.setopt(cURL.URL, url + '/cloud/elastic/disable/' + command_list[2])
        cURL.perform()
    else:
        print('Usage: cloud disable <pod_id>')

def main():
    rm_url = 'http://10.140.17.126:3000'
    while(1):
        command = input('$ ')
        if command == 'cloud init':
            cloud_init(rm_url)
        elif command.startswith('cloud pod register'):
            cloud_pod_register(rm_url)
        elif command.startswith('cloud pod rm'):
            cloud_pod_rm(rm_url)
        elif command.startswith('cloud register'):
            cloud_register(rm_url, command)
        elif command.startswith('cloud rm'):
            cloud_rm(rm_url, command)
        elif command.startswith("cloud launch"):
            cloud_launch(rm_url, command)
        elif command.startswith("cloud resume"):
            cloud_resume(rm_url, command)
        elif command.startswith("cloud pause"):
            cloud_pause(rm_url, command)
        elif command.startswith("cloud lower"):
            cloud_set_lower(rm_url, command)
        elif command.startswith("cloud upper"):
            cloud_set_upper(rm_url, command)
        elif command.startswith("cloud enable"):
            cloud_enable_elastic(rm_url, command)
        elif command.startswith("cloud disable"):
            cloud_disable_elastic(rm_url, command)
        elif command.startswith("q"):
            break
if __name__ == '__main__':
    main()