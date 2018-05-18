#!/bin/bash
if [ $# -eq 0 ]
  then
    echo "No script supplied."
    echo "Run any of the following: ap_prepare, ap_train, ap_detect"
  exit 1
fi

poetry run $@
