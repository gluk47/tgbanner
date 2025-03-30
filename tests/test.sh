#!/bin/bash -x

test_root="$(dirname "$BASH_SOURCE")"
cd "$test_root"

PYTHONPATH="$(readlink -f ..)" pytest test_tgbanner.py

