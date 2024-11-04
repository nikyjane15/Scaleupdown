import requests
import time
import sys, os
from fabric import Connection
import threading
import pandas as pd
import json


# caso 0 ->  Is when we have a test with nothing running on top of it.
#           I take the counters at the beginning and at the end of test
# case 1 ->  Is when we have a test with up and down scaling for multiple times.
#           I take counter before the test, when the test is running every 10 minutes, and at the end


# distinguere il caso 0 e il caso 1
# Case 0 -> prendi prima tutti i counter, poi fai partire il programma sul 192.168.17.28 e alla fine lo fai andare
# Case 1 -> qui devi cercare di sincronizzare, nel senso che qui fai andare lo scale up and down

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect("192.168.254.82","22","ubuntu","pap3rin0")
# commands = ['mkdir cipolla1, cd cipolla1, touch banana.txt']
# stdin, stdout, stderr = ssh.exec_command(commands)

def json_to_csv_energy(energy_counter):
    df = pd.DataFrame()
    for element in energy_counter:
        data = json.loads(element)
        print(data)
        energies = [data[x].get('value') for x in range(0, len(data))]
        if df.empty:
            physical = pd.Series(data[x].get('name') for x in range(0, len(data)))
            df = pd.DataFrame(columns=physical)
        df.loc[len(df)] = energies


# creates csv files for counter
def json_to_csv_cstate(cstate_counters):
    for host in cstate_counters:
        for element in cstate_counters[host]:
            data = json.loads(cstate_counters[host][element])
            print(data)
            df = pd.DataFrame.from_dict(data)
            filename = "results/" + host.replace(".maas","") + element + ".csv"
            df.to_csv(filename)


def run_scale_up_down():
    sys.stdout = open(os.devnull, 'w')
    with c.cd('/home/ubuntu/pktgen'):
        result1 = c.run('./client_exe client.yaml /home/ubuntu/.kube/config')


def get_energy():
    # sys.stdout = sys.__stdout__
    for index, name in enumerate(hostname):
        r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + name)
        x = r.text
        print(x)
        energy_counter.append(r.text)
    print('Energy acquired')


def get_counters(cstate_counters):
    for index, name in enumerate(hostname):
        for idx, i in enumerate(counters_name):
            r = requests.get(URL + "/api/CPUGovernor/" + counters_name[idx] + "?hostName=" + name)
            cstate_counters[name][i] = r.text


test_type = 0
timer = 0
URL = "http://192.168.254.15:8001"
hostname = ["r2hpgen8-test.maas", "r1hpgen9-2.maas"]
ip_client = "192.168.17.28"
ip_server_k8 = "192.168.17.29"

c = []
# other one
counters_name = ["Cstates-Usage", "Cstates-Time"]
energy_name = "EnergyRapl"
cstate_counters_start = cstate_counters_end = {"r2hpgen8-test.maas":
    {
        "Cstates-Usage": "",
        "Cstates-Time": ""
    },
    "r1hpgen9-2.maas":
        {
            "Cstates-Usage": "",
            "Cstates-Time": ""
        }}
energy_counter_temp = [
    '[{"name":"PhysicalGroup0","value":10880519608,"unit":"µJ"},{"name":"PhysicalGroup1","value":13464443064,"unit":"µJ"},{"name":"PhysicalGroup2","value":11819328006,"unit":"µJ"},{"name":"PhysicalGroup3","value":58246204018,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":11080097391,"unit":"µJ"},{"name":"PhysicalGroup1","value":13676306467,"unit":"µJ"},{"name":"PhysicalGroup2","value":12027067767,"unit":"µJ"},{"name":"PhysicalGroup3","value":58513945314,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":11279001655,"unit":"µJ"},{"name":"PhysicalGroup1","value":13879528821,"unit":"µJ"},{"name":"PhysicalGroup2","value":12258426362,"unit":"µJ"},{"name":"PhysicalGroup3","value":58749286628,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":11482226482,"unit":"µJ"},{"name":"PhysicalGroup1","value":14082597727,"unit":"µJ"},{"name":"PhysicalGroup2","value":12497426148,"unit":"µJ"},{"name":"PhysicalGroup3","value":58968721447,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":11681418146,"unit":"µJ"},{"name":"PhysicalGroup1","value":14298070745,"unit":"µJ"},{"name":"PhysicalGroup2","value":12722453863,"unit":"µJ"},{"name":"PhysicalGroup3","value":59186957796,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":11884542270,"unit":"µJ"},{"name":"PhysicalGroup1","value":14525562520,"unit":"µJ"},{"name":"PhysicalGroup2","value":12928674918,"unit":"µJ"},{"name":"PhysicalGroup3","value":59404622321,"unit":"µJ"}]',
    '[{"name":"PhysicalGroup0","value":14118453782,"unit":"µJ"},{"name":"PhysicalGroup1","value":16794902239,"unit":"µJ"},{"name":"PhysicalGroup2","value":15213098666,"unit":"µJ"},{"name":"PhysicalGroup3","value":62219069729,"unit":"µJ"}]']
energy_counter = []

c.append(Connection(host="ubuntu@" + ip_client, connect_kwargs={"password": "pap3rin0"}))
# take the initial counters of CPU usage and Time
get_counters(cstate_counters_start)
get_energy()
# take the energies counters of CPU usage and Time
match test_type:
    case 0:
        print("Case no scaling is going on")
        # time.sleep(43200)      #12 hours in seconds

    case 1:
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     f1 = executor.submit(run_scale_up_down())
        p1 = threading.Thread(target=run_scale_up_down)
        p1.start()
        while timer < 5:
            time.sleep(10)  # da mettere 600 e cambiare il range del timer
            get_energy()
            timer += 1
        p1.join()

sys.stdout = sys.__stdout__
#get_counters(cstate_counters_end)
# get_energy()
json_to_csv_cstate(cstate_counters_start)
#json_to_csv_cstate(cstate_counters_end)
# json_to_csv_energy(energy_counter)
