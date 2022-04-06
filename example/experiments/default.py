from example.evaluators.main import some_evaluator
from example.executors.main import some_experiment


experiments = {
    "default-experiment": {
        "executor": some_experiment,
        "evaluators": [some_evaluator],
        "arg1": "Hello",
        "arg2": "World",
    },
    "abstract-experiment": {
        "executor": some_experiment,
        "evaluators": [some_evaluator],
        "abstract": True,
        "arg1": "Hello",
        "arg2": "World",
    },
}
