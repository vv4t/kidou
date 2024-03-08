#!/bin/sh

if [ $# -lt 1 ]
then
  echo "usage: $0 <file> [--dump]"
  exit 1
fi

python src/cc/cc.py $@
