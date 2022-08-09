#!/bin/bash

output=${1}


actual=$(grep "Correct" ${output} | awk '{print $7}')
total=$(grep "Correct" ${output} | awk '{print $9}')

actual=(${actual})
total=(${total})

if [[ ${actual[0]} -ne ${total[0]} ]]; then
  echo "Some stories failed"
  exit 1
fi

if [[ ${actual[1]} -ne ${total[1]} ]]; then
  echo "Some stories failed"
  exit 1
fi