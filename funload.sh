#!/bin/bash

echo "+===============================+"
echo "| $(date) |"
echo "+-------------------------------+"
. .funload/config
python ${funloadPath}/funload.py
echo
