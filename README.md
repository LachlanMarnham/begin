# `begin` - v0.4.0
[![image](https://img.shields.io/pypi/v/begin-cli.svg)](https://pypi.org/project/begin-cli/)
[![image](https://img.shields.io/pypi/l/begin-cli.svg)](https://pypi.org/project/begin-cli/)
[![image](https://img.shields.io/pypi/pyversions/begin-cli.svg)](https://pypi.org/project/begin-cli/)
![tests](https://github.com/LachlanMarnham/begin/actions/workflows/tests.yml/badge.svg?branch=master)
![flake8](https://github.com/LachlanMarnham/begin/actions/workflows/flake8.yml/badge.svg?branch=master)
[![codecov](https://codecov.io/gh/LachlanMarnham/begin/branch/master/graph/badge.svg)](https://codecov.io/gh/LachlanMarnham/begin)


## Usage
```bash
begin <target_name>@<registry_name> [<key>:<value>]
```
1. Arguments to be passed to targets should take the form `<arg_name>:<arg_value>`
2. Registry names must not contain a colon
3. Target names must not contain a colon or an `@`
4. If a target name, registry name or argument value contains whitespace, it must be
wrapped in single quotes.


## Contributing
Although the `targets.py` contains recipes for installing dependencies, they cannot be
executed until `begin` is installed. To resolve the chicken-and-egg problem, get started
with:

```bash
pip install --upgrade pip
poetry install
```

Following this initial setup, dependency changes can be picked up with

```bash
begin install
```
