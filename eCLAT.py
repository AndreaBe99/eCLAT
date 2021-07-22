#!/usr/bin/python3
# -*- coding: utf-8 -*-

__title__ = "eCLAT"
__version__ = "2.0"
__status__ = "unreleased"
__author__ = "Andrea Bernini"
__date__ = "2021 Giugno 16"


from engine import EclatEngine
import argparse

def run(fname):
    with open(fname) as f:
        text_input = f.read()
    engine = EclatEngine(fname.split("/")[-1])
    engine.run(text_input)

def main():
    # parse argument
    parser = argparse.ArgumentParser(description='Eclat Parser')
    parser.add_argument('-r', '--run', action="store", help="Eclat script to run", required=True)

    args = vars(parser.parse_args())

    print(args)
    ret = run(args['run'])
    #print(ret)
    return ret


if __name__ == "__main__":
    main()