import requests
import time
import paramiko
from fabric import Connection
import threading

#caso 0 ->  Is when we have a test with nothing running on top of it.
#           I take the counters at the beginning and at the end of test
#case 1 ->  Is when we have a test with up and down scaling for multiple times.
#           I take counter before the test, when the test is running every 10 minutes, and at the end

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect("192.168.254.82","22","ubuntu","pap3rin0")
# commands = ['mkdir cipolla1, cd cipolla1, touch banana.txt']
# stdin, stdout, stderr = ssh.exec_command(commands)
def run_scale_up_down():
    with c.cd('/home/ubuntu/pktgen'):
        result1 = c.run('./client_exe client.yaml /home/ubuntu/.kube/config')

def energy_counter(energy_counter):
    time.sleep(600)
    r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + hostname)
    energy_counter.append(r)


test_type = 0
timer = 0
URL = "http://192.168.13.5:8001"
hostname = "r2hpgen8-test.maas" #need to add the
# other one
counters_name = ["Cstates-Usage", "Cstates-Time"]
energy_name = "EnergyRapl"
start_counter = []
energy_counter = []
endCounter = []

c = Connection(host="ubuntu@192.168.17.28", connect_kwargs={"password": "pap3rin0"})
#take the initial couters of CPU usage and Time
for idx, i in enumerate(counters_name):
    r = requests.get(URL + "/api/CPUGovernor/" + counters_name[idx] + "?hostName=" + hostname)
    start_counter.append(r)

#take the energies couters of CPU usage and Time
match test_type:
    case 0:
        r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + hostname)
        energy_counter.append(r)
        print("start_sleep")
        while timer < 12:
            time.sleep(600)
            r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + hostname)
            energy_counter.append(r)
            timer += 1
    case 1:
        r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + hostname)
        energy_counter.append(r)
        print("start_sleep")
        while timer < 12:
            time.sleep(600)
            r = requests.get(URL + "/api/CPUGovernor/" + energy_name + "?hostName=" + hostname)
            energy_counter.append(r)
            timer += 1