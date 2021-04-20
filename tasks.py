#!/usr/bin/env python3
# Standard Library
import inspect
import os
import sys
from pathlib import Path
from subprocess import run


def _inspect_tasks(prefix):
    return {
        f[0].replace(prefix, ""): f[1]
        for f in inspect.getmembers(sys.modules["__main__"], inspect.isfunction)
        if f[0].startswith(prefix)
    }


def _cmd(command, args=[]):
    return run(command.split(" ") + args)


def _pycmd(command, args=[]):
    # TODO: make this cross platform
    py3 = ".venv/bin/python3"
    return run([py3, "-m"] + command.split(" ") + args)


def _exit_handler(status):
    statuses = status if type(status) == list else [status]
    bad_statuses = [s for s in statuses if s.returncode != 0]
    if bad_statuses:
        sys.exit(bad_statuses)


def task_init(args):
    results = []
    results.append(_cmd("python3 -m venv .venv"))
    results.append(_pycmd("pip install --upgrade pip setuptools wheel"))
    results = results + [
        _pycmd(f"pip install -r {req} --upgrade", args)
        for req in ["requirements.txt", "requirements-dev.txt"]
        if Path(req).is_file()
    ]
    return results


def task_install(args):
    return [
        _pycmd(f"pip install -r {req} --upgrade", args)
        for req in ["requirements.txt", "requirements-dev.txt"]
        if Path(req).is_file()
    ]


def task_qa(args):
    targets = ["mydash/", "tasks.py"]
    return [_pycmd(f"{tool} {' '.join(targets)}") for tool in ["black", "isort", "flake8"]]


def task_test(args):
    return _pycmd("pytest", args)


def task_dev(args):
    return _pycmd("mydash", args)


def task_logs(args):
    # Third Party Libraries
    from dotenv import load_dotenv

    load_dotenv()
    return _cmd(f"heroku logs -a {os.getenv('APP_NAME')}", args)


if __name__ == "__main__":
    tasks = _inspect_tasks("task_")

    if len(sys.argv) >= 2 and sys.argv[1] in tasks.keys():
        _exit_handler(tasks[sys.argv[1]](sys.argv[2:]))
    else:
        print(f"Must provide a task from the following: {list(tasks.keys())}")
