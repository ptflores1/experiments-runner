import os
from collections import defaultdict
from itertools import chain

from experiments_runner.utils import dynamic_import, listdir_abs


class ExperimentsLoader:
    experiment_reserved_words = [
        "extends",
        "executor",
        "evaluators",
        "abstract",
    ]
    non_inheritable_fields = ["abstract"]
    required_fields = ["executor"]

    def __init__(self, experiments_paths: str) -> None:
        self.experiments_paths = experiments_paths
        self.experiments = self.parse_experiments()
        self.resolve_experiments_dependencies()
        self.validate_experiments()

    def check_unique_experiments(self, experiments_list):
        names = set()
        for exp_name in chain.from_iterable(experiments_list):
            # Check unique names
            if exp_name in names:
                raise Exception(f"Experiment name '{exp_name}' is not unique.")

    def validate_experiments(self):
        # Check required fields
        for name, exp in self.experiments.items():
            if not exp.get("abstract", False):
                for field in self.required_fields:
                    if field not in exp:
                        raise Exception(f"Required field '{field}' not found in experiment '{name}'.")

    def parse_experiments(self):
        paths = self.experiments_paths
        if not isinstance(self.experiments_paths, list):
            if not os.path.isdir(self.experiments_paths):
                raise Exception(
                    f"experiments_paths should be list of files or a directory instead found {self.experiments_paths}."
                )
            else:
                paths = list(filter(lambda x: x.endswith(".py"), listdir_abs(self.experiments_paths)))

        experiments_list = []
        for path in paths:
            experiments_list.append(dynamic_import(path).experiments)

        self.check_unique_experiments(experiments_list)

        experiments = {}
        for exps in experiments_list:
            experiments.update(exps)

        return experiments

    def resolve_experiments_dependencies(self):
        children = defaultdict(list)
        for key, val in self.experiments.items():
            if "extends" in val:
                parents = val["extends"] if isinstance(val["extends"], list) else [val["extends"]]
                for parent_name in parents:
                    children[parent_name].append(key)

        stack = [key for key, val in self.experiments.items() if "extends" not in val]
        while len(stack):
            curr = stack.pop()
            if "extends" in self.experiments[curr]:
                parents = self.experiments[curr]["extends"]
                inherited_fields = {
                    k: v
                    for parent in parents
                    for k, v in self.experiments[parent].items()
                    if k not in self.non_inheritable_fields
                }
                inherited_fields.update(self.experiments[curr])
                self.experiments[curr] = inherited_fields
            stack += children[curr]

    def get_kwargs(self, params_dict):
        kwargs = {key: val for key, val in params_dict.items() if key not in self.experiment_reserved_words}
        return kwargs

    def get_experiment_args(self, experiment_name: str):
        experiment = self.experiments[experiment_name]
        return self.get_kwargs(experiment)
