import subprocess
import threading
import signal
import os
import time
from argparse import ArgumentParser
from py import process
import yaml


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


running_processes = dict()


def read_config(config_path):
    with open(config_path) as file:
        configs = yaml.load(file, Loader=yaml.FullLoader)

    if "python-exec" not in configs or configs["python-exec"] is None:
        configs["python-exec"] = "python"
        print("python-exec is not set in config.yaml, uses 'python' as default value")
    if "processes" not in configs:
        raise ValueError("There is no processes provided in config.yaml")
    if "states" not in configs or configs["states"] is None:
        configs["states"] = [{"default": [k for k in configs["processes"]]}]
        print("states is not set in config.yaml, created state 'default' with all processes started")

    python_exec = configs["python-exec"]
    
    processes = list()
    process_names = set()
    for name, conf in configs["processes"].items():
        if "exec_path" not in conf or "conda_env" not in conf:
            raise ValueError("Process '%s' in config.yaml must contain both 'exec_path' and 'conda_env' fields" % name)
        if not isinstance(conf["exec_path"], str):
            raise ValueError("Value of 'exec_path' in process '%s' must be string" % name)
        if not isinstance(conf["conda_env"], str):
            raise ValueError("Value of 'conda_env' in process '%s' must be string" % name)
        env_name = conf["conda_env"]
        script_path = os.path.normpath(conf["exec_path"])
        process_names.add(name)
        processes.append((name, env_name, script_path))
    
    states = configs["states"]
    for state, procs in configs["states"].items():
        if not set(procs).issubset(process_names):
            raise ValueError("Some processes in state '%s' are not included in processes" % state)

    return python_exec, processes, states


def run_new_process(env_name, python_exec, script_path, process_name, color):
    print(color + "Starting %s..." % process_name + bcolors.ENDC)
    print_tag = color + "%15s | " % process_name + bcolors.ENDC
    cmds = ["conda", "activate", env_name, "&&", python_exec, script_path, "&&", "conda", "deactivate"]

    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', shell=True)
    running_processes[process_name] = p

    while True:
        output = p.stdout.readline()
        if output == '' and p.poll() is not None:
            break
        if output:
            print(print_tag + output.rstrip("\n"), flush=True)
    print(color + "%s has stopped" % process_name + bcolors.ENDC)

    running_processes.pop(process_name, None)


def main(args):
    p_count = 0
    colors = [bcolors.OKPURPLE, bcolors.OKBLUE, bcolors.OKCYAN, bcolors.OKGREEN, bcolors.OKYELLOW]
    python_exec, processes, states = read_config(args["configpath"])
    for (process_name, env_name, script_path) in processes:
        if process_name not in running_processes or running_processes[process] is None:
            s = threading.Thread(target=run_new_process, args=(env_name, python_exec, script_path, process_name, colors[p_count % len(colors)]))
            s.start()
            p_count += 1
    
    ### Start Testing ###
    time.sleep(10)
    print(running_processes)
    running_processes["process1"].send_signal(signal.CTRL_C_EVENT)
    time.sleep(1)
    print(running_processes)
    s = threading.Thread(target=run_new_process, args=("testenv", "python", "test.py", "process1", colors[p_count % len(colors)]))
    s.start()
    p_count += 1
    time.sleep(5)
    print(running_processes)
    ### End Testing ###


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", "--fileconfig", dest="configpath", default="config.yaml",
                        help="path to configurations .yaml file", metavar="FILEPATH")
    args = vars(parser.parse_args())
    os.environ["PYTHONUNBUFFERED"] = "1"
    main(args)