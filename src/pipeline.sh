#!/usr/bin/env zsh
# first download past week's data and filter based on length
DIR=$(mktemp -d)
DATA=$PWD/../database
./get_reddit_data.sh $DIR
# run diagnosis of thought on downloaded data
for FILE in $DIR; do
  new_dot.py "$FILE.json"
done
# merge all json files into one
jq -s 'add' $DIR/*.json $DATA/database.json | jq 'unique' > $DIR/database.json.tmp
mv $DIR/database.json.tmp $DATA/database.json
