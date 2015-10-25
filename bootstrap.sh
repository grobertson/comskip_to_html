#!/bin/sh

virtualenv --python=/usr/bin/python3 env3
. env3/bin/activate
pip install -r requirements3.txt
