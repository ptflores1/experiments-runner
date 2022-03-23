import os
from pprint import pprint
from experiments_runner.runner import ExperimentsRunner


current_folder = os.path.dirname(os.path.abspath(__file__))
experiments_path = os.path.join(current_folder, "experiments")
print("Experiments Path:", experiments_path)
runner = ExperimentsRunner(experiments_paths=experiments_path)
runner.resolve_experiments_dependencies()
pprint(runner.experiments)
