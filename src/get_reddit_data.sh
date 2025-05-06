#!/usr/bin/env zsh
# We need to test this after the api is fixed

DIR=$1
SUBS="depression GriefSupport grief bereavement loneliness lonely mentalhealth Life Vent Anxiety emotionalabuse ptsd cptsd selfharm suicidewatch unsentletters offmychest helpmecope adulting relationships divorce childhoodtrauma raisedbynarcissists regret guilt cancer chronicpain infertility petloss povertyfinance nihilism existentialism confessions trueoffmychest sad"
DATA_DIR=$PWD/../database/
WD=$PWD
seconds_in_day=864000
num_iterations=7 #One week of data

cd $DIR
for sub in $SUBS; do
  if test -e "$sub.json"; then
    echo "File $sub.json already exists. Skipping subreddit: $sub"
    continue
  fi
  echo "Processing subreddit: $sub"
  before_epoch=`date +%s`
  for i in $(seq 1 $num_iterations); do
    after_epoch=$((before_epoch - seconds_in_day))
    echo "  Iteration: $i, sub: $sub"
    curl "https://api.pullpush.io/reddit/search/submission/?size=1000&subreddit=$sub&before=$before_epoch&after=$after_epoch&sort_type=num_comments" 2>/dev/null \
      | jq '.data[].selftext' 2>/dev/null \
      | gsed -e 's/^"//' -e 's/"$//' \
      | gawk 'NF < 4 || NF > 250 { next } { print }' \
      >> "$sub"
    before_epoch=$after_epoch
  done
  cat $sub | uniq | jq -sR 'split("\n")[:-1] | map({text: ., source: "r/'$sub'", state: "unfiltered"})' > "$sub.json"
  echo "Finished processing subreddit: $sub"
done

echo "Data collection complete."
cd $WD

# run the python script to filter the data
