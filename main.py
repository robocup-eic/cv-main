import subprocess
import threading
import os
import time
import socket
from argparse import ArgumentParser
import yaml
from custom_socket import CustomSocket


class bcolors:
    OKPURPLE = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    OKYELLOW = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'



colors = [bcolors.OKPURPLE, bcolors.OKBLUE, bcolors.OKGREEN, bcolors.OKYELLOW, bcolors.OKCYAN]
p_count = 0
configs = dict()
running_processes = dict()
current_state = None


def read_config(config_path):
    with open(config_path) as file:
        configs = yaml.load(file, Loader=yaml.FullLoader)

    if "port" not in configs or configs["port"] is None:
        configs["port"] = 15000
        print("port is not set in config.yaml, uses 15000 as default port")
    if not isinstance(configs["port"], int):
        raise ValueError("Value of 'port' in config.yaml must be integer")
    if "conda-exec" not in configs or configs["conda-exec"] is None:
        configs["conda-exec"] = "conda"
        print("conda-exec is not set in config.yaml, uses 'conda' as default value")
    if "processes" not in configs:
        raise ValueError("There is no processes provided in config.yaml")
    if "states" not in configs or configs["states"] is None:
        configs["states"] = [{"default": [k for k in configs["processes"]]}]
        print("states is not set in config.yaml, created state 'default' with all processes started")

    configs["conda-exec"] = os.path.normpath(configs["conda-exec"])
    
    process_names = set()
    for name, conf in configs["processes"].items():
        if "exec_cmd" not in conf or "conda_env" not in conf:
            raise ValueError("Process '%s' in config.yaml must contain both 'exec_cmd' and 'conda_env' fields" % name)
        if not isinstance(conf["exec_cmd"], str):
            raise ValueError("Value of 'exec_cmd' in process '%s' must be string" % name)
        if not isinstance(conf["conda_env"], str):
            raise ValueError("Value of 'conda_env' in process '%s' must be string" % name)
        process_names.add(name)
    
    for state, procs in configs["states"].items():
        if not set(procs).issubset(process_names):
            raise ValueError("Some processes in state '%s' are not included in processes" % state)

    return configs


def run_new_process(env_name, exec_cmd, process_name, conda_exec="conda", color=bcolors.OKBLUE):
    global running_processes

    print(color + "Starting %s..." % process_name + bcolors.ENDC)
    print_tag = color + "%15s | " % process_name + bcolors.ENDC
    cmds = [conda_exec, "run", "-n", env_name, "--no-capture-output"] + exec_cmd.split(" ")

    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', shell=False)
    running_processes[process_name] = p

    print(color + "%s has started (%d)" % (process_name, p.pid) + bcolors.ENDC)
    while True:
        if p.poll() is not None:
            break
        output = p.stdout.readline()
        if output:
            print(print_tag + output.rstrip("\n"), flush=True)
    print(color + "%s (%d) has stopped" % (process_name, p.pid) + bcolors.ENDC)

    running_processes.pop(process_name, None)


def change_state(desired_state):
    global p_count, current_state, configs, running_processes

    if current_state is not None:
        p_current = set(configs["states"][current_state])
    else:
        p_current = set()
    p_target = set(configs["states"][desired_state])
    p_term = p_current - p_target
    p_start = p_target - p_current

    for process_name in p_term:
        running_processes[process_name].terminate()
    for process_name in p_start:
        env_name = configs["processes"][process_name]["conda_env"]
        exec_cmd = configs["processes"][process_name]["exec_cmd"]
        if process_name not in running_processes or running_processes[process_name] is None:
            s = threading.Thread(
                target=run_new_process,
                args=(env_name, exec_cmd, process_name, configs["conda-exec"], colors[p_count % len(colors)])
                )
            s.start()
            p_count += 1
    
    current_state = desired_state


def main(args):
    global configs
    configs = read_config(args["configpath"])
    change_state("default")
    
    server = CustomSocket(socket.gethostname(), configs["port"])
    server.startServer()
    while True:
        conn, addr = server.sock.accept()
        print("Client connected from", addr)
        while True:
            msg = server.recvMsg(conn)
            try:
                state = msg.decode("utf-8")
                change_state(state)
                print("State changed to %s from client %s", state, addr)
            except:
                print("Message received with error:", msg, type(msg))

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--fileconfig", dest="configpath", default="config.yaml",
                        help="path to configurations .yaml file", metavar="FILEPATH")
    args = vars(parser.parse_args())
    os.environ["PYTHONUNBUFFERED"] = "1"
    main(args)