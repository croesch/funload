#!/bin/bash

DIR="$(cd "$(dirname "${0}")" && pwd)"

echo "Installing funload"
echo "  - creating config directory"
mkdir ~/.funload

echo "  - copying default configs"
for file in $(ls "${DIR}/config")
do
  echo "    -> ${file}"
  cp -a "${file}" "~/.funload"
done

echo "  - store path to executable"
echo "funloadPath=\"${DIR}\"" > ~/.funload/config

BFILE="/tmp/$(basename $0).$$.backup"
TFILE="/tmp/$(basename $0).$$.tmp"
echo "  - backing up crontab to '${BFILE}'"
crontab -l > ${BFILE}

echo "  - adding entry in crontab"
crontab -l > ${TFILE}
echo "$(shuf -i 0-60 -n 1) * * * * "${DIR}/funload.sh" >> funload.log 2>&1" >> ${TFILE}
crontab ${TFILE}
rm ${TFILE}

echo "  - creating target directory ~/funload/"
mkdir ~/funload

echo "done. Ready for fun!"
echo
echo "Funload will automatically load stuff into ~/funload/"
echo "So keep an eye on that :-)"
echo "No further actions required..."
echo 
echo "+---------------------------------------------------------+"
echo "| IMPORTANT NOTE: DO NOT MOVE THE DIRECTORY OF FUNLOAD!!! |"
echo "+---------------------------------------------------------+"
