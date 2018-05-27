#!/bin/bash

source ~/dev/.virtualenv/esgp/bin/activate
cd $(dirname $0)
cat /dev/stdin | python3 -m esgp $*
