#!/bin/bash
# shellcheck disable=SC1012
output_dir=$1
youtuber=$2
#./get_wenet_output/generate_separated_wav_transcript.sh "/Users/bennettlee/Desktop/ITN Pipeline" "Chris @HoneyMoneySG"

python get_wenet_output/generate_separated_wav_transcript.py --json "${output_dir}"/"${youtuber}"/vtt_env.json
#  -i "D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\wav" \
#  -t "D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_text_with_times" \
#  -o "D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_wav"
#

sleep 20