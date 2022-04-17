import subprocess
import threading
import os
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


def read_config():
    with open("config.yaml") as file:
        configs = yaml.load(file, Loader=yaml.FullLoader)
    
    output = list()
    for name, conf in configs.items():
        if "exec_path" not in conf or "conda_env" not in conf:
            raise ValueError("Model '%s' in config.yaml must contain both 'exec_path' and 'conda_env' fields" % name)
        if not isinstance(conf["exec_path"], str):
            raise ValueError("Value of 'exec_path' in model '%s' must be string" % name)
        if not isinstance(conf["conda_env"], str):
            raise ValueError("Value of 'conda_env' in model '%s' must be string" % name)
        env_name = conf["conda_env"]
        script_path = os.path.normpath(conf["exec_path"])
        output.append((name, env_name, script_path))
    return output


def run_new_process(env_name, script_path, process_name, color):
    print(color + "Starting %s..." % process_name + bcolors.ENDC)
    print_tag = color + "%15s | " % process_name + bcolors.ENDC
    cmds = ["conda", "activate", env_name, "&&", "python", script_path, "&&", "conda", "deactivate"]

    p = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8', shell=True)
    while True:
        output = p.stdout.readline()
        if output == '' and p.poll() is not None:
            break
        if output:
            print(print_tag + output.rstrip("\n"), flush=True)
    print(color + "%s has stopped" % process_name + bcolors.ENDC)


def main():
    colors = [bcolors.OKPURPLE, bcolors.OKBLUE, bcolors.OKCYAN, bcolors.OKGREEN, bcolors.OKYELLOW]
    configs = read_config()
    for i, (process_name, env_name, script_path) in enumerate(configs):
        s = threading.Thread(target=run_new_process, args=(env_name, script_path, process_name, colors[i % len(colors)]))
        s.start()


if __name__ == "__main__":
    os.environ["PYTHONUNBUFFERED"] = "1"
    main()