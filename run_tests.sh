#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

echo -e "\nFlake8"
echo "#########################"
./flake8-diff.py --changed --verbose
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
