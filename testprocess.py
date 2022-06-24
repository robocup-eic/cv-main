import subprocess
import threading
import os
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


def run_new_process(env_name, script_path, process_name, conda_exec="conda", python_exec="python", color=bcolors.OKBLUE):
    print(color + "Starting %s..." % process_name + bcolors.ENDC)
    print_tag = color + "%15s | " % process_name + bcolors.ENDC
    cmds = [conda_exec, "activate", env_name, "&&", python_exec, script_path]

    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', shell=False)
    running_processes[process_name] = p

    while True:
        output = p.stdout.readline()
        if output:
            print(print_tag + output.rstrip("\n"), flush=True)
        if p.poll() is not None:
            break
    print(color + "%s has stopped" % process_name + bcolors.ENDC)

    running_processes.pop(process_name, None)


os.environ["PYTHONUNBUFFERED"] = "1"
s = threading.Thread(target=run_new_process, args=("testenv", "test.py", "process1", r"D:\ProgramData\Anaconda3\Library\bin\conda.bat"))
s.start()
s = threading.Thread(target=run_new_process, args=("testenv", "test.py", "process2", r"D:\ProgramData\Anaconda3\Library\bin\conda.bat"))
s.start()
s = threading.Thread(target=run_new_process, args=("testenv", "test.py", "process3", r"D:\ProgramData\Anaconda3\Library\bin\conda.bat"))
s.start()
time.sleep(5)
running_processes["process1"].terminate()
s = threading.Thread(target=run_new_process, args=("testenv", "test.py", "process1", r"D:\ProgramData\Anaconda3\Library\bin\conda.bat"))
s.start()