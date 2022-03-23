import os
from pprint import pprint
from experiments_runner.runner import ExperimentsRunner


current_folder = os.path.dirname(os.path.abspath(__file__))
experiments_path = os.path.join(current_folder, "experiments")
runner = ExperimentsRunner(experiments_paths=experiments_path)
pprint(runner.experiments)
