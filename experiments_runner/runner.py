from collections import defaultdict
from itertools import chain
import os

from .utils import listdir_abs, dynamic_import


class ExperimentsRunner:
    def __init__(self, experiments_paths) -> None:
        self.experiments_paths = experiments_paths
        self.experiments = self.parse_experiments()
        self.resolve_experiments_dependencies()

    def parse_experiments(self):
        paths = self.experiments_paths
        if not isinstance(self.experiments_paths, list):
            if not os.path.isdir(self.experiments_paths):
                raise Exception(
                    f"experiments_paths should be list of files or a directory instead found {self.experiments_paths}"
                )
            else:
                paths = list(
                    filter(
                        lambda x: x.endswith(".py"), listdir_abs(self.experiments_paths)
                    )
                )

        experiments_list = []
        for path in paths:
            experiments_list.append(dynamic_import(path).experiments)

        names = set()
        for exp_name in chain.from_iterable(experiments_list):
            if exp_name in names:
                raise Exception(f"Experiment name '{exp_name}' is not unique.")

        experiments = {}
        for exps in experiments_list:
            experiments.update(exps)
        return experiments

    def resolve_experiments_dependencies(self):
        children = defaultdict(list)
        for key, val in self.experiments.items():
            if "extends" in val:
                children[val["extends"]].append(key)

        stack = [key for key, val in self.experiments.items() if "extends" not in val]
        while len(stack):
            curr = stack.pop()
            if "extends" in self.experiments[curr]:
                parent = self.experiments[curr]["extends"]
                self.experiments[curr].update(self.experiments[parent])
            stack += children[curr]

    def run(self):
        pass
