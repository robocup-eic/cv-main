import subprocess
import time
import signal


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