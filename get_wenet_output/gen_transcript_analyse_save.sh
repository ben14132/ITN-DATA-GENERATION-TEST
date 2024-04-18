#!/bin/bash
# Author: Zin
# Date: Aug 2022
# Desc: A script to generate transcripts from online ASR (WeNET) from a given audio dir
# Usage: bash script.sh <input-wav-dir> <asr-port-num> <output-exp-dir>
# E.g. bash script.sh ./testdata/imda-part2/wav 8015 1 ./exp/exp-imdapart2-modelname

wav_path=$1
port=$2
hw=$3
expid=$4
ground_truth_path=$5

ip=20.198.234.55

# Create exp dir
mkdir -p $expid
rm -r $expid/*.txt

read_mode=nocont
# Generate transcript
# transcribe each wav in $wav_path
# transcript.txt is saved in the $wav_path
#original: do for wav in "$url_name"/wav/*.wav;
for url_name in "$wav_path"/*;
  do for wav in "$url_name"/*;
    do
      echo $wav
      if [ "$read_mode" ==  nocont ];
        then
          echo "$wav"
          echo "\n\n\n\n"
          echo "mode:"
          read -r read_mode
      fi
      #changed hw from $hw to 0
      python get_wenet_output/gen_transcript_analyse_save.py -r 16000 -hw $hw -u ws://$ip:$port --ground-truth "$ground_truth_path" --output "$expid" "$wav";
  done;
done;


#for wav in "$wav_path"/*.wav;
#  do
#    if [ "$read_mode" ==  nocont ];
#      then
#        echo "$wav"
#        echo "mode:"
#        read -r read_mode
#    fi
#  python gen_transcript_analyse_save.py -r 16000 -hw $hw -u ws://$ip:$port --ground-truth "$ground_truth_path" --output "$expid" "$wav";
#done;

# example:  bash gen_transcript_analyse_save.sh ./testdata/0927/wav 8016 0 ./exp/0927 ./testdata/0927
# gen_transcript_analyse_save.sh "D:\study\singaporeMasters\master project\data\wav_by_sentence" 8016 0 ./exp/1201
# gen_transcript_analyse_save.sh "D:/study/singaporeMasters/master_project/term2/data/youtube_crawler/Chris@HoneyMoneySG/segmented_wav" 8016 0 "D:/study/singaporeMasters/master_project/term2/data/youtube_crawler/Chris@HoneyMoneySG/wenet_transcript_2"
# ./get_wenet_output/gen_transcript_analyse_save.sh "/Users/bennettlee/Desktop/ITNPipeline2/ASR input" 8016 0 "/Users/bennettlee/Desktop/ITNPipeline2/ASR output"
# asr input folder can only have wav folder, no other transcript folder if not wav folder will not be detected
sleep 10