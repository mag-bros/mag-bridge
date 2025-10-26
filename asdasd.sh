#!/bin/bash
# simple example.sh

NAME="World"
COUNT=3

for ((i=1; i<=COUNT; i++)); do
echo "Hello, $NAME! ($i)"
done

if [ "$COUNT" -gt 2 ]; then
  echo "That's enough greetings."
fi
