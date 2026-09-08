#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows Task Scheduler setup for Property Listing Manager.

Usage:
    python setup_scheduler.py setup
    python setup_scheduler.py list
    python setup_scheduler.py run
    python setup_scheduler.py test
    python setup_scheduler.py delete
"""

import argparse
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(r"C:\Users\maart\Documents\Property listing manager")
COLLECTOR_SCRIPT = BASE_DIR / "listing_collector.py"
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"

TASK_NAME = "PropertyListingManagerDaily"
RUN_TIME = "10:00"


def get_python_executable():
    """Use the project virtual environment Python when it exists."""
    if VENV_PYTHON.exists():
        return VENV_PYTHON

    return Path(sys.executable)


def run_command(command):
    """Run a command and print stdout/stderr in a readable way."""
    result = subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.stderr:
        print(result.stderr.strip())

    return result.returncode


def build_task_action():
    """Build the command that Windows Task Scheduler should run."""
    python_executable = get_python_executable()

    return f'"{python_executable}" "{COLLECTOR_SCRIPT}"'


def setup_task():
    """Create or update the daily Windows scheduled task."""
    if not COLLECTOR_SCRIPT.exists():
        print(f"Collector script not found: {COLLECTOR_SCRIPT}")
        return 1

    task_action = build_task_action()

    command = [
        "schtasks",
        "/Create",
        "/TN",
        TASK_NAME,
        "/TR",
        task_action,
        "/SC",
        "DAILY",
        "/ST",
        RUN_TIME,
        "/F",
    ]

    print(f"Creating scheduled task: {TASK_NAME}")
    print(f"Schedule: every day at {RUN_TIME}")
    print(f"Action: {task_action}")

    return run_command(command)


def list_task():
    """Show detailed information about the scheduled task."""
    command = [
        "schtasks",
        "/Query",
        "/TN",
        TASK_NAME,
        "/V",
        "/FO",
        "LIST",
    ]

    return run_command(command)


def run_task():
    """Run the scheduled task immediately through Windows Task Scheduler."""
    command = [
        "schtasks",
        "/Run",
        "/TN",
        TASK_NAME,
    ]

    print(f"Starting scheduled task now: {TASK_NAME}")
    return run_command(command)


def test_collector():
    """Run the collector immediately in the current terminal."""
    python_executable = get_python_executable()

    command = [
        str(python_executable),
        str(COLLECTOR_SCRIPT),
    ]

    print("Running collector directly for testing.")
    print(f"Python: {python_executable}")
    print(f"Script: {COLLECTOR_SCRIPT}")

    return run_command(command)


def delete_task():
    """Delete the Windows scheduled task."""
    command = [
        "schtasks",
        "/Delete",
        "/TN",
        TASK_NAME,
        "/F",
    ]

    print(f"Deleting scheduled task: {TASK_NAME}")
    return run_command(command)


def main():
    parser = argparse.ArgumentParser(
        description="Manage the Property Listing Manager scheduled task."
    )
    parser.add_argument(
        "command",
        choices=["setup", "list", "run", "test", "delete"],
        help=(
            "setup=create/update task, list=show task, run=start scheduled task, "
            "test=run collector directly, delete=remove task"
        ),
    )

    args = parser.parse_args()

    if args.command == "setup":
        return setup_task()

    if args.command == "list":
        return list_task()

    if args.command == "run":
        return run_task()

    if args.command == "test":
        return test_collector()

    if args.command == "delete":
        return delete_task()

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
