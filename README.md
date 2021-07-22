# eclat-finish-vs
## Prerequisites

Python 3.5 or higher
pip version 9.0.1 or higher
If necessary, upgrade your version of pip:

```shell
$ python -m pip install --upgrade pip
```

If you cannot upgrade pip due to a system-owned installation, you can run the example in a virtualenv:

```shell
$ python -m pip install virtualenv
$ virtualenv venv
$ source venv/bin/activate
$ python -m pip install --upgrade pip
```

## Install

```shell
pip install -r requirements.txt
```

## Run

```shell
./eclat.py --run nomescript.eclat
./eclat.py -r nomescript.eclat
```

## Unit test

```shell
python -m unittest test.test_parser
```
