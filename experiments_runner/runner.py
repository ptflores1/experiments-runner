from collections import defaultdict
from itertools import chain
import os
import shutil
from typing import List, Literal, Union

from .utils import WorkingDirectory, listdir_abs, dynamic_import

EXPERIMENTS_TO_RUN_TYPES = Union[List[str], Literal["all", "new"]]


class ExperimentsRunner:
    def __init__(
        self,
        experiments_paths: str,
        results_folder: str,
        experiments_to_run: EXPERIMENTS_TO_RUN_TYPES = "new",
    ) -> None:
        self.experiments_paths = experiments_paths
        self.experiments = self.parse_experiments()
        self.resolve_experiments_dependencies()

        self.experiments_to_run = experiments_to_run

        self.results_folder = results_folder
        if not os.path.exists(results_folder):
            os.mkdir(results_folder)

        self.experiment_reserved_words = [
            "extends",
            "experiment_function",
            "evaluators",
            "abstract",
        ]

    def check_unique_experiments(self, experiments_list):
        names = set()
        for exp_name in chain.from_iterable(experiments_list):
            # Check unique names
            if exp_name in names:
                raise Exception(f"Experiment name '{exp_name}' is not unique.")

    def validate_experiments(self, experiments):
        # Check required fields
        required_fields = ["experiment_function"]
        for name, exp in experiments.items():
            for field in required_fields:
                if field not in exp:
                    raise Exception(
                        f"Required field '{field}' not found in experiment '{name}'."
                    )

    def parse_experiments(self):
        paths = self.experiments_paths
        if not isinstance(self.experiments_paths, list):
            if not os.path.isdir(self.experiments_paths):
                raise Exception(
                    f"experiments_paths should be list of files or a directory instead found {self.experiments_paths}."
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

        self.check_unique_experiments(experiments_list)

        experiments = {}
        for exps in experiments_list:
            experiments.update(exps)

        self.validate_experiments(experiments)
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

    def get_kwargs(self, params_dict):
        kwargs = {
            key: val
            for key, val in params_dict.items()
            if key not in self.experiment_reserved_words
        }
        return kwargs

    def run(self):
        to_run = self.experiments.items()
        if isinstance(self.experiments_to_run, list):
            to_run = filter(lambda x: x[0] in self.experiments_to_run, to_run)

        should_overwrite = self.experiments_to_run == "all" or isinstance(
            self.experiments_to_run, list
        )

        for name, params in to_run:
            if not params.get("abstract", False):
                experiment_path = os.path.join(self.results_folder, name)
                exp_exists = os.path.exists(experiment_path)
                if exp_exists and self.experiments_to_run == "new":
                    print(
                        f"Skipping experiment '{name}', results folder already exists."
                    )
                else:
                    print(f"Running experiment '{name}'.")
                    if should_overwrite and exp_exists:
                        print(f"Overwriting existing folder for experiment '{name}'.")
                        shutil.rmtree(experiment_path)

                    os.mkdir(experiment_path)
                    kwargs = self.get_kwargs(params)
                    try:
                        with WorkingDirectory(experiment_path):
                            result = params["experiment_function"](**kwargs)

                            for evaluator in params["evaluators"]:
                                print(f"Running evaluator '{evaluator.__name__}'.")
                                evaluator(result)
                    except Exception as e:
                        print(
                            f"Experiment '{name}' raised the exception: '{type(e).__name__}: {e}'."
                        )
            else:
                print(f"Skipping abstract experiment '{name}'.")
            print("#" * 50)
