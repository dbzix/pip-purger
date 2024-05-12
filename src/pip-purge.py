#!/usr/bin/env python3

import argparse
import signal
import subprocess
import sys
from subprocess import CompletedProcess, SubprocessError
from typing import Any, NamedTuple

_PKG_NAME = "Name:"
_REQUIRES = "Requires:"
_REQUIRED_BY = "Required-by:"

# these packages should be removed directly by pip, and will be skipped by pip-purger
_WHITELIST = ["pip", "pip-purger", "setuptools", "wheel"]

_GRAY_COLOR = "\x1b[38;2;128;128;128m"
_NO_COLOR = "\x1b[0m"


class PackageInfo(NamedTuple):
    package_name: str
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


def find_removable_dependencies(package: str) -> list[str]:
    """Check specified package for whitelist and possible errors,
    then search for all removable dependencies and return them as an iterable.
    """
    if package in _WHITELIST:
        print(f"Use native 'pip' command to remove following packages: {', '.join(_WHITELIST)}")
        exit(0)

    try:
        # support removal of only single package at the moment
        package_info = get_package_infos(package)[0]
    except PackageCheckError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    if package_info.required_by:
        print(f"Package '{package}' is required by: {', '.join(package_info.required_by)}.")
        print(
            f"{_GRAY_COLOR}"
            f"You may run 'pip list --not-required'"
            f" to list packages that are not dependencies of installed packages."
            f"{_NO_COLOR}"
        )
        exit(1)

    removables = {package}
    dependencies = package_info.requires - set(_WHITELIST)  # exclude whitelisted dependencies
    if dependencies:
        print(f"Gathering '{package}' dependencies...")
        # update removables recursively
        _check_dependencies(*dependencies, removables=removables)

    return sorted(removables - {package})


def get_package_infos(*packages: str) -> list[PackageInfo]:
    """Get and return package information for the specified packages."""
    pip_process = _run_pip_command("show", *packages)
    pip_output = pip_process.stdout
    if not pip_output:
        raise PackageCheckError(pip_process.stderr.rstrip())

    package_summaries = (package for package in pip_output.split("\n---\n"))
    package_infos_str = (
        (
            line.strip()
            for line in package_summary.splitlines()
            if any(
                line.strip().startswith(prefix) for prefix in (_PKG_NAME, _REQUIRES, _REQUIRED_BY)
            )
        )
        for package_summary in package_summaries
    )
    return [
        PackageInfo(
            _parse_package_name(package_name),
            _parse_requires(requires_str),
            _parse_required_by(required_by_str),
        )
        for package_name, requires_str, required_by_str in package_infos_str
    ]


def _parse_package_name(package_name_str: str) -> str:
    """Parse 'Name: ...' string in the 'pip show ...' output for a package."""
    return package_name_str.lstrip(_PKG_NAME).strip().lower()


def _parse_requires(requires_str: str) -> set[str]:
    """Parse 'Requires: ...' string in the 'pip show ...' output for a package."""
    requires = requires_str.lstrip(_REQUIRES).strip()
    return set() if requires == "" else set(str.split(requires.lower(), ", "))


def _parse_required_by(required_by_str: str) -> set[str]:
    """Parse 'Required-by: ...' string in the 'pip show ...' output for a package."""
    required_by = required_by_str.lstrip(_REQUIRED_BY).strip()
    return set() if required_by == "" else set(str.split(required_by.lower(), ", "))


def _check_dependencies(*packages: str, removables: set[str]) -> None:
    """Recursively check packages and all their dependencies for removable ones.
    Put removable dependencies and their removable sub-dependencies into `removables`.

    Package is removable only when it is needed by requested packages or by packages
    in `removables`, and nowhere else. Otherwise, the package is not removable.
    """
    try:
        package_infos = get_package_infos(*packages)
    except PackageCheckError as ex:
        print(ex, file=sys.stderr)
        sys.exit(1)

    sub_dependencies = set()
    for package_info in package_infos:
        if not (package_info.required_by - removables):
            # current package is not required anywhere else, but only by our removables
            removables.add(package_info.package_name)
            sub_dependencies.update(package_info.requires)

    sub_dependencies -= set(_WHITELIST)  # exclude whitelisted sub-dependencies
    if sub_dependencies:
        _check_dependencies(*sub_dependencies, removables=removables)


def uninstall(package: str, *dependencies: str) -> None:
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
    pip_command: str, *arguments: str, capture_output: bool = True
) -> CompletedProcess[str]:
    """Run pip command with the arguments provided.
    If `capture_output` flag is set to `True`, then sub-process output will be encapsulated into
    the return value.
    Otherwise, `stdout` and `stderr` of sub-process will be both re-directed to `sys.stdout`.
    """
    # print(f"Executing: '{pip_command}' with arguments: {arguments}")  # for debug purposes
    output_args: dict[str, Any] = (
        {} if capture_output else {"stdout": sys.stdout, "stderr": sys.stdout}
    )
    try:
        return subprocess.run(
            [sys.executable, "-m", "pip", pip_command, *arguments],
            text=True,
            capture_output=capture_output,
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
    uninstall(package_name, *package_dependencies)


if __name__ == "__main__":
    main()
