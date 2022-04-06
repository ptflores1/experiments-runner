import os


def some_experiment(arg1, arg2):
    print(arg1, arg2)

    os.mkdir("checkpoints")
    with open("./checkpoints/chk1.txt", "w") as f:
        f.write("someline")
    return "Successfully ran experiment"
