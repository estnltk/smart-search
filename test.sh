#!/bin/bash

PORT=$1

for i in {1..1000}
do
    curl -s --request POST --header "Content-Type: application/json"  localhost:${PORT}/settings > /dev/null &
done
echo ""
