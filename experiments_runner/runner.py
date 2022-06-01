import os
import inspect
import shutil
import traceback
from typing import List, Literal, Union

from experiments_runner.experiments_loader import ExperimentsLoader
from .utils import WorkingDirectory

MODE_TYPES = Union[List[str], Literal["all", "new"]]


class ExperimentsRunner:
    def __init__(
        self,
        experiments_paths: str,
    ) -> None:
        self.experiments_loader = ExperimentsLoader(experiments_paths)

    def filter_kwargs(self, kwargs, targets):
        return {target: kwargs.get(target) for target in targets}

    def run(
        self,
        results_folder: str,
        overwrite_kwargs: dict = None,
        mode: MODE_TYPES = "new",
    ):
        if not os.path.exists(results_folder):
            os.mkdir(results_folder)

        to_run = self.experiments_loader.experiments.items()
        if isinstance(mode, list):
            to_run = filter(lambda x: x[0] in mode, to_run)

        should_overwrite = mode == "all" or isinstance(mode, list)
        print("Loaded experiments:")
        for name, _ in to_run:
            print(f"    - {name}")
        print()
        for name, params in to_run:
            if not params.get("abstract", False):
                experiment_path = os.path.join(results_folder, name)
                exp_exists = os.path.exists(experiment_path)
                if exp_exists and mode == "new":
                    print(f"Skipping experiment '{name}', results folder already exists.")
                else:
                    print(f"Running experiment '{name}'.")
                    if should_overwrite and exp_exists:
                        print(f"Overwriting existing folder for experiment '{name}'.")
                        shutil.rmtree(experiment_path)

                    os.mkdir(experiment_path)
                    kwargs = self.experiments_loader.get_kwargs(params, overwrite_kwargs)
                    try:
                        with WorkingDirectory(experiment_path):
                            executor_args = inspect.getfullargspec(params["executor"]).args
                            filtered_kwargs = self.filter_kwargs(kwargs, executor_args)
                            result = params["executor"](**filtered_kwargs)

                            for evaluator in params["evaluators"]:
                                print(f"Running evaluator '{evaluator.__name__}'.")
                                if "executor_args" in inspect.getfullargspec(evaluator).args:
                                    evaluator(result, executor_args=kwargs)
                                else:
                                    evaluator(result)
                    except Exception as e:
                        print(
                            f"Experiment '{name}' raised the exception: '{type(e).__name__}: {e}'. Printing stack trace:"
                        )
                        print(traceback.format_exc())
            else:
                print(f"Skipping abstract experiment '{name}'.")
            print("#" * 50)
