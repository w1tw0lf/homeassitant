from typing import final
from pyunifi.controller import Controller
from datetime import timedelta
import json
import re

#### fill in your unifi controller credentials ####

host = 'ip/url'
username = 'username'
password = 'password'
version = 'UDMP-unifiOS'
site_id = 'default'
port = '443'
verify_ssl = True

################# endpoints ####################

client = Controller(host, username, password, port, version,
                          site_id=site_id, ssl_verify=verify_ssl)
unifi_devices = client.get_aps()

device = []
for du in range(len(unifi_devices)):
    adopted = unifi_devices[du]['adopted']
    if adopted == True:
        device.append({unifi_devices[du]['mac']})

active_device = []
for d in range(len(device)):
    target_mac = unifi_devices[d]['mac']
    stat = client.get_sysinfo()
    devs = client.get_device_stat(target_mac)
    clients = client.get_clients()
    cpu = devs['system-stats']['cpu']
    ram = devs['system-stats']['mem']
    model = devs['model']
    type = devs['type']
    name = devs['name']
    update = devs['upgradable']
    activity = round(devs['uplink']['rx_bytes-r']/125000 + devs['uplink']['tx_bytes-r']/125000,1)
    seconds = devs['uptime']
    days = seconds // 86400
    hours = (seconds - (days * 86400)) // 3600
    minutes = (seconds - (days * 86400) - (hours * 3600)) // 60
    uptime = str(days)+'d '+str(hours)+'h '+str(minutes)+'m'
    device_info = []
    if type == 'usw':
        usedports = devs['num_sta']
        userports = devs['user-num_sta']
        guestports = devs['guest-num_sta']
        ports = []
        for x in range(len(devs['port_table'])):
            port = devs['port_table'][x]['up']
            if port == True:
                ports.append(True)
            else:
                ports.append(False)
        device_name = name.replace(' ', '_')
        active_device.append(device_name)
        output_filename_ports = 'device_' + device_name + '_ports.json'
        active_ports= []
        for ap in range(len(ports)):
            active_ports.append({"Port" + str(ap+1):ports[ap]})
        activeports = json.dumps(active_ports)  
        with open(output_filename_ports, 'w') as a_p:
            a_p.write(activeports) 
        results = json.dumps({"Friendly name":name,"Model":model,"Type":type,"Activity":str(activity)+' Mbps',"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Ports_used":usedports,"Ports_user":userports,"Ports_guest":guestports,"Update":update})
        output_filename = 'device_' + device_name + '.json'
        with open(output_filename, 'w') as output:
            output.write(results)

    elif type == 'uap':
        numclients = devs['user-wlan-num_sta']
        numguests = devs['guest-wlan-num_sta']
        score = devs['satisfaction']
        wifi0clients = devs['radio_table_stats'][0]['user-num_sta']
        wifi1clients = devs['radio_table_stats'][1]['user-num_sta']
        wifi0score = devs['radio_table_stats'][0]['satisfaction']
        wifi1score = devs['radio_table_stats'][1]['satisfaction']
        results = json.dumps({"Friendly name":name,"Model":model,"Type":type,"Clients":numclients,"Guests":numguests,"Clients_wifi0":wifi0clients ,"Clients_wifi1":wifi1clients ,"Score":score,"CPU":str(cpu),"RAM":str(ram),"Uptime":uptime,"Score_wifi0":wifi0score ,"Score_wifi1":wifi1score ,"Activity":str(activity)+' Mbps',"Update":update})
        device_name = name.replace(' ', '_')
        active_device.append(device_name)
        output_filename = 'device_' + device_name + '.json'
        with open(output_filename, 'w') as output:
            output.write(results)

index = 0 
device_results = []      
while index < len(active_device):
        device_results.append({"Device" + str(index+1):active_device[index]})
        index = index + 1
deviceresults = json.dumps(device_results)
output_filename = 'devices.json'
with open(output_filename, 'w') as output:
    output.write(deviceresults)

print(deviceresults)

