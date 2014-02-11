#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

flake8 .
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
