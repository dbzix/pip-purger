
# Pip Purger

Are you still struggling with dangling `pip` dependencies?
Struggle no more!

**Pip Purger** aims to uninstall your packages leaving no garbage behind.


## Installation

Clone the project:

```bash
  $ git clone https://github.com/dbzix/pip-purger
```

Create a symlink to the executable in your private `bin` directory:

```bash
  $ ln -s $(realpath -s pip-purger/src/pip-purge.py) ~/.local/bin/pippurge
```

Test it:
```bash
$ pippurge 
usage: pippurge <package>
pippurge: error: the following arguments are required: package
```

<details>
<summary>Doesn't work?</summary>

You ran it, but it doesn't work:

```bash
$ pippurge
pippurge: command not found
```

Ensure that your *shell* puts your private `bin` directory into the `PATH` variable:

```bash
$ echo $PATH | tr ":" "\n"
# ...
# ...
/home/username/.local/bin
# ...
# ...
```

Cannot find? Fix it:

```bash
$ cat .bashrc
# ...
# ...
# ...
# modify PATH to include user's local binaries directory if it exists
if [ -d "$HOME/.local/bin" ] ; then
  PATH="$HOME/.local/bin:$PATH"
fi
```
</details>

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

> **Note**: Remember to always use [virtual environments](https://realpython.com/python-virtual-environments-a-primer/)!

## Do you like Pip Purger?
Feel free to support my work:

| Cryptocurrency | Address |
| --- | --- |
| Bitcoin (BTC) | bc1qwf90w004z04v39emd3jj8q4ev4rdna739ecqj5 |
| Ethereum (ETH)| 0xED726ADA8d6A4f908de77f689D918039b03a698C |
| Ripple (XRP) |rH8CFA1QVaijiMBaL9FgbpTzu2rYsu3FgB |
| TON / USDT on TON | UQCVsW7ygTvQWmf8xRwMST7AdfDzNxwrw0CYkThEfhA5Xsk6 |
