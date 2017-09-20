#!/bin/bash
touch usbreader.txt
truncate -s 0 usbreader.txt
for d in /media/$USER/*/; do
    readlink -f $d >> usbreader.txt
done
