from example.evaluators.main import some_evaluator
from example.experiment_functions.main import some_experiment


experiments = {
    "default-experiment": {
        "experiment_function": some_experiment,
        "evaluators": [some_evaluator],
        "arg1": "Hello",
        "arg2": "World",
    },
    "abstract-experiment": {
        "experiment_function": some_experiment,
        "evaluators": [some_evaluator],
        "abstract": True,
        "arg1": "Hello",
        "arg2": "World",
    },
}
