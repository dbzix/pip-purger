#!/usr/bin/env python3

import argparse
import signal
import subprocess
import sys
from subprocess import CompletedProcess, SubprocessError
from typing import Iterable, NamedTuple

_REQUIRES = "Requires:"
_REQUIRED_BY = "Required-by:"

# these packages should be removed directly by pip, and will be skipped by pip-purger
_WHITELIST = ["pip", "pip-purger", "setuptools", "wheel"]

_GRAY_COLOR = "\x1b[38;2;128;128;128m"
_NO_COLOR = "\x1b[0m"


class PackageInfo(NamedTuple):
    requires: set[str]
    required_by: set[str]


class PackageCheckError(OSError):
    pass


def process_arguments() -> str:
    """Process command line args."""
    parser = argparse.ArgumentParser(
        description="Removes specified package with all unused dependencies.",
        usage="%(prog)s <package>",
    )
    parser.add_argument(
        "package",
        help="Package to remove",
    )
    args = parser.parse_args()
    return args.package


def find_removable_dependencies(package: str) -> Iterable[str]:
    """Check specified package for whitelist and possible errors,
    then search for all removable dependencies and return them as an iterable.
    """
    if package in _WHITELIST:
        print(f"Use native 'pip' command to remove following packages: {', '.join(_WHITELIST)}")
        exit(0)

    try:
        package_info = get_package_info(package)
    except PackageCheckError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    if package_info.required_by:
        print(f"Package '{package}' is required by '{', '.join(package_info.required_by)}'.")
        print(
            f"{_GRAY_COLOR}"
            f"You may run 'pip list --not-required'"
            f" to list packages that are not dependencies of installed packages."
            f"{_NO_COLOR}"
        )
        exit(1)

    removables = {package}
    for dependency in package_info.requires:
        # update removables recursively
        _check_dependencies(dependency, removables)

    return sorted(removables - {package})


def get_package_info(package: str) -> PackageInfo:
    """Get package information for the specified package."""
    pip_process = _run_pip_command("show", package)
    pip_output = pip_process.stdout
    if not pip_output:
        raise PackageCheckError(pip_process.stderr.decode().rstrip("\n"))

    requires_str, required_by_str = [
        dependency.strip()
        for dependency in bytes.decode(pip_output).split("\n")
        if any(dependency.strip().startswith(substr) for substr in (_REQUIRES, _REQUIRED_BY))
    ]

    return PackageInfo(
        _parse_requires(requires_str),
        _parse_required_by(required_by_str),
    )


def _parse_requires(requires_str: str) -> set[str]:
    """Parse 'Requires: ...' string in the 'pip show ...' output for a package."""
    requires = requires_str.lstrip(_REQUIRES).strip()
    return set() if requires == "" else set(str.split(requires.lower(), ", "))


def _parse_required_by(required_by_str: str) -> set[str]:
    """Parse 'Required-by: ...' string in the 'pip show ...' output for a package."""
    required_by = required_by_str.lstrip(_REQUIRED_BY).strip()
    return set() if required_by == "" else set(str.split(required_by.lower(), ", "))


def _check_dependencies(package: str, removables: set[str]) -> None:
    """Recursively check package and all its dependencies for removable dependencies.
    Put removable dependencies and their removable sub-dependencies into `removables`.
    """
    if package in _WHITELIST:
        return

    try:
        package_info = get_package_info(package)
    except PackageCheckError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    if not (package_info.required_by - removables):
        # current package is not required anywhere else, but only by our removables
        removables.add(package)

    for dependency in package_info.requires:
        _check_dependencies(dependency, removables)


def uninstall(package: str, dependencies: Iterable[str]) -> None:
    """Uninstall package with its dependencies."""
    print(f"Package '{package}' will be uninstalled", end="")
    print(f" with its dependencies: {', '.join(dependencies)}." if dependencies else ".")

    if not confirm("Proceed (y/N)? "):
        return

    _run_pip_command("uninstall", "-y", package, *dependencies, capture_output=False)


def confirm(prompt: str) -> bool:
    """Confirm user choice."""
    return input(prompt) in ("y", "Y")


def _run_pip_command(
    pip_command: str, *arguments: Iterable[str], capture_output: bool = True
) -> CompletedProcess[bytes]:
    """Run pip command with the arguments provided.
    If `capture_output` flag is set to `True`, then sub-process output will be encapsulated into
    the return value.
    Otherwise, `stdout` and `stderr` of sub-process will be both re-directed to `sys.stdout`.
    """
    output_args = (
        {"capture_output": capture_output}
        if capture_output
        else {"stdout": sys.stdout, "stderr": sys.stdout}
    )
    try:
        return subprocess.run(
            [sys.executable, "-m", "pip", pip_command, *arguments],
            **output_args,
        )
    except SubprocessError as ex:
        print(f"Failed to run pip: {ex}", file=sys.stderr)
        sys.exit(1)


def _sigint_handler(*_):
    """Handler for 'Interrupt from keyboard' signal or SIGINT (Ctrl+C)."""
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGQUIT, _sigint_handler)

    package_name = process_arguments()
    package_dependencies = find_removable_dependencies(package_name)
    uninstall(package_name, package_dependencies)


if __name__ == "__main__":
    main()
