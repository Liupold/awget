#!/bin/sh

python -m pip install requests parameterized python-magic
python 'tests/test_name_resolver.py' ; exit "$?"
