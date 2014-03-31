#!/bin/bash
DIR=$(cd -P -- "$(dirname -- "$0")" && pwd -P)

RETURN=0
cd $DIR

if [ -n "$*" ]; then
    TESTS="$@"
else
    TESTS="kgkeystone"
fi

# NOTE (RS) Disabled because there are far too many errors to fix.

echo -e "\nFlake8"
echo "#########################"
if [[ "$DH_INTERNAL_OVERRIDE" != 'dh_auto_test' ]]
then
    ./flake8-diff.py --changed --verbose
    if [ ! $? -eq 0 ]
    then
        RETURN=1
    fi
fi

echo -e "\n\nTests"
echo "#########################"
./manage.py test --settings=karaage.tests.settings -v 2 $TESTS
if [ ! $? -eq 0 ]
then
    RETURN=1
fi

exit $RETURN
