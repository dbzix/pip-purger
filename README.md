
# Pip Purger

Are you still struggling with dangling `pip` dependencies?
Struggle no more!

**Pip Purger** aims to uninstall your packages leaving no garbage behind.


## Installation

Clone the project

```bash
  $ git clone https://github.com/dbzix/pip-purger
```

Go to the project directory

```bash
  $ cd path/to/pip-purger
```

Make pip-purger.py executable

```bash
  $ chmod +x src/pip-purger.py
```

Create shared symlink to the executable

```bash
  $ ln -s $(realpath -s src/pip-purge.py) ~/.local/bin/pippurge
```

## Usage
```
$ pippurge flask
Gathering 'flask' dependencies...
Package 'flask' will be uninstalled with its dependencies: blinker, itsdangerous, jinja2, markupsafe, werkzeug.
Proceed (y/N)? y
Found existing installation: Flask 3.0.3
Uninstalling Flask-3.0.3:
  Successfully uninstalled Flask-3.0.3
Found existing installation: blinker 1.8.2
Uninstalling blinker-1.8.2:
  Successfully uninstalled blinker-1.8.2
Found existing installation: itsdangerous 2.2.0
Uninstalling itsdangerous-2.2.0:
  Successfully uninstalled itsdangerous-2.2.0
Found existing installation: Jinja2 3.1.4
Uninstalling Jinja2-3.1.4:
  Successfully uninstalled Jinja2-3.1.4
Found existing installation: MarkupSafe 2.1.5
Uninstalling MarkupSafe-2.1.5:
  Successfully uninstalled MarkupSafe-2.1.5
Found existing installation: Werkzeug 3.0.3
Uninstalling Werkzeug-3.0.3:
  Successfully uninstalled Werkzeug-3.0.3
```
