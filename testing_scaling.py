import json
import threading
import time
import os, sys

import pandas as pd
import requests
from fabric import Connection
import paramiko

import configuration


# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect("192.168.254.82","22","ubuntu","pap3rin0")
# commands = ['mkdir cipolla1, cd cipolla1, touch banana.txt']
# stdin, stdout, stderr = ssh.exec_command(commands)

def json_to_csv_energy(energy_counter):
    for host in energy_counter:
        df = pd.DataFrame()
        for element in energy_counter[host]:
            data = json.loads(element)
            energies = [str(data[x].get('value')) for x in range(0, len(data))]
            if df.empty:
                physical = pd.Series(data[x].get('name') + "(" + data[x].get('unit') + ")" for x in range(0, len(data)))
                df = pd.DataFrame(columns=physical)
            df.loc[len(df)] = energies
        filename = "results/" + host.replace(".maas", "") + "_energies" + ".csv"
        df.to_csv(filename)

def get_result_files():
    ssh_client = paramiko.SSHClient()

# creates csv files for counter
def json_to_csv_cstate(cstate_counters, pos):
    for host in cstate_counters:
        for element in cstate_counters[host]:
            data = json.loads(cstate_counters[host][element])
            df = pd.DataFrame.from_dict(data)
            filename = "results/" + host.replace(".maas", "") + "_" + element + "_" + pos + ".csv"
            df.to_csv(filename)


def run_scale_up_down():
    # sys.stdout = open(os.devnull, 'w')
    with c.cd('/home/ubuntu/pktgen-13'):
        result1 = c.run('./client_exe client.yaml /home/ubuntu/.kube/config')


def get_energy(energy_counter_param):
    # sys.stdout = sys.__stdout__
    for index, name in enumerate(hostname):
        r = requests.get(url + "/api/CPUGovernor/" + energy_name + "?hostName=" + name)
        x = r.text
        energy_counter_param[name].append(x)
    print('Energy acquired')


def get_counters(cstate_counters):
    for index, name in enumerate(hostname):
        for idx, i in enumerate(counters_name):
            r = requests.get(url + "/api/CPUGovernor/" + counters_name[idx] + "?hostName=" + name)
            cstate_counters[name][i] = r.text


test_type = configuration.case
timer = 0
url = configuration.URL
hostname = configuration.hostname
ip_client = configuration.ip_client
ip_server_k8 = configuration.ip_server_k8
time_test = configuration.time_test
counters_name = configuration.counters_name
max_timer_count = int(configuration.time_test / 600)

c = []
energy_name = "EnergyRapl"
cstate_counters_start = cstate_counters_end = \
    {hostname[0]:
        {
            counters_name[0]: "",
            counters_name[1]: ""
        },
        hostname[1]:
            {
                counters_name[0]: "",
                counters_name[1]: ""
            }
    }

energy_counter = {hostname[0]: [],
                  hostname[1]: []}

c = Connection(host="ubuntu@" + ip_client, connect_kwargs={"password": "pap3rin0"})
# take the initial counters of CPU usage and Time
start_time = time.perf_counter()
get_counters(cstate_counters_start)
get_energy(energy_counter)
# take the energies counters of the master and worker
match test_type:
    case 0:
        print("Case no scaling is going on")
        # time.sleep(time_test)      #12 hours in seconds
        while timer < 10:  # put max_timer_count instead 100
            time.sleep(5)  # da mettere 600 e cambiare il range del timer
            get_energy(energy_counter)
            timer += 1

    case 1:
        print("Scaling is going on")
        p1 = threading.Thread(target=run_scale_up_down)
        p1.start()
        while timer < 10:  # put max_timer_count instead 100
            time.sleep(5)  # da mettere 600 e cambiare il range del timer
            get_energy(energy_counter)
            timer += 1
        p1.join()

end_time = time.perf_counter()
print(f"Start Time:{start_time:.0f}")
print(f"End Time:{end_time:.0f}")
print(f"Performance time: {end_time-start_time:.0f}")
get_counters(cstate_counters_end)
get_energy(energy_counter)

# conversion to csv
json_to_csv_cstate(cstate_counters_start, pos="start")
json_to_csv_cstate(cstate_counters_end, pos="end")
json_to_csv_energy(energy_counter)
