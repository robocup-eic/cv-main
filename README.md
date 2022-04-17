# Computer Vision Initialization Script

Note: Running with real models are not tested yet. (18/04/2022)

## Prerequisites

* python >= 3.8.5 (For running main.py)
    * python 3.6 should be fine, although it is tested with python 3.8.5
* conda as environment manager
* pyyaml library

## Installation

You should install each model as described on each model's `README.md`

* Object Detection: https://github.com/robocup-eic/robocup2022-cv-object-detection
* What Is That: https://github.com/robocup-eic/robocup2022-cv-what-is-that
* Person Tracker: https://github.com/robocup-eic/robocup2022-cv-person-tracker

Each of the model's libraries must be configured through conda environment from `requirements.txt` provided in each repository.

```bash
# Create new conda env
conda create --name "<env_name>" python="<version>"
# Activating newly created env
conda activate "<env_name>"
# Install lib using conda
conda install --file "<requirements.txt>"
# Install lib using pip
pip install -r "<requirements.txt>"
# Coming back to base env
conda deactivate
```

Take note of each model's file path and environment name, you will have to edit the `config.yaml` using these settings.

## Configuration

Edit the `config.yaml` with each model's main script file path and the conda environment name.

```yaml
model1:
  conda_env: "<model1_env_name>"
  exec_path: "<main_file_to_execute.py>"
model2:
  conda_env: "<model2_env_name>"
  exec_path: "<main_file_to_execute.py>"
```

Each model must be provided with `conda_env` and `exec_path`. The `exec_path` can be either absolute or relative. Multiple models (or any process/program actually) can be appended to the `config.yaml` as shown in the above example.

## Executing

Start: Run python script as normal

```bash
python main.py
```

Stop: Type CTRL+C in the terminal console

## Socket API Servers

* Object Detection: `tcp://localhost:10001`
* What Is That: `tcp://localhost:10000`
* Person Tracker: `tcp://localhost:11000`

For API Syntax, please refer to each repository.