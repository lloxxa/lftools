#!/bin/bash
declare -A arr
shopt -s globstar

for file in **; do
  [[ -f "$file" ]] || continue
   
  read cksm _ < <(md5 "$file")
  if ((arr[$cksm]++)); then 
    rm $file
  fi
done

