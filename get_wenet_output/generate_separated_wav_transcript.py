import io
import os
import argparse
import shutil

from pydub import audio_segment
from ws4py.client.threadedclient import WebSocketClient
import time
import threading
import sys
import urllib.parse
import queue
import json
import time
import os
import datetime
import pyaudio
import ssl
import pathlib

sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')


# input: 00:00:00.000
def getTimeStamp(input: str) -> int:
    ret = 0
    split = input.split(':')
    print(split[0])
    print(split[1])
    print(split[2])
    ret = int(float(split[0])) * 3600 * 1000 + int(float(split[1])) * 60 * 1000 + int(float(split[2]) * 1000)
    return ret


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--json", required=True)

    args = parser.parse_args()

    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)
    # parser.add_argument('-i', '--inputfolder', default='', dest='input_folder',
    #                     help='the input folder of wav files to cut')
    # parser.add_argument('-t', '--transcriptfolder', default='', dest='transcript_folder', help='the transcript folder')
    # parser.add_argument('-o', '--outputfile', default='', dest='output_folder',
    #                     help='the output folder of cut wavfiles, default is current folder')
    # args = parser.parse_args()
    #
    # print(args)
    #
    # args.input_folder = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\wav"
    # args.transcript_folder = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_text_with_times"
    # args.output_folder = r"D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_wav"

    input_folder = config['generate_separated_wav_transcript']['input_folder']
    transcript_folder = config['generate_separated_wav_transcript']['transcript_folder']
    output_folder = config['generate_separated_wav_transcript']['output_folder']



    transcripts = dict()
    for transcript in os.listdir(transcript_folder):
        # transcripts[transcript.split('.')[0]] = transcript
        transcripts[transcript[:11]] = transcript

    k = transcripts.keys()
    # print(k)

    out_wav_folder = os.path.join(output_folder, 'wav')
    out_transcript_folder = os.path.join(output_folder, 'transcript')
    if not os.path.exists(out_wav_folder):
        os.makedirs(out_wav_folder)
    else:
        shutil.rmtree(out_wav_folder, ignore_errors=True)
    if not os.path.exists(out_transcript_folder):
        os.makedirs(out_transcript_folder)
    else:
        shutil.rmtree(out_transcript_folder, ignore_errors=True)


    for file in os.listdir(input_folder):
        if file.endswith('.wav'):
            print(file[:-4])
            if not file[:-4] in transcripts.keys():
                continue

            # this is for generation by audio.
            # new_output_folder = os.path.join(output_folder, file[:-4])
            # new_output_wav_folder = os.path.join(new_output_folder, 'wav')
            # if not os.path.exists(new_output_folder):
            #     os.makedirs(new_output_folder)
            # else:
            #     shutil.rmtree(new_output_folder, ignore_errors=True)
            # if not os.path.exists(new_output_wav_folder):
            #     os.makedirs(new_output_wav_folder)
            # else:
            #     shutil.rmtree(new_output_wav_folder, ignore_errors=True)

            # this is clustering all audio result in one folder
            wav_file_path = os.path.join(input_folder, file)
            transcript_file_path = os.path.join(transcript_folder, transcripts[file[:-4]])

            wav = audio_segment.AudioSegment.from_wav(wav_file_path)

            with open(transcript_file_path, 'r+') as f:
                lines = f.readlines()
                for line in lines:
                    print(line)
                    splitted = line.split()
                    print(splitted)
                    # start = int(float(splitted[0]) * 1000)
                    # end = int(float(splitted[1]) * 1000)
                    print(splitted[0][1:-1])
                    start = getTimeStamp(splitted[0][1:-1])
                    end = getTimeStamp(splitted[1][1:-1])
                    print(f'{start} {end}')
                    cur_transcript = ' '.join(splitted[2:])
                    cur_wav = wav[start: end]
                    new_wav_name = file[:-4] + '_' + str(start).zfill(6) + '_' + str(end).zfill(6) + '.wav'
                    new_transcript_name = file[:-4] + '_' + str(start).zfill(6) + '_' + str(end).zfill(6) + '.txt'
                    cur_wav.export(os.path.join(out_wav_folder, new_wav_name), format='wav')
                    with open(os.path.join(out_transcript_folder, new_transcript_name), 'w+') as f:
                        f.writelines(cur_transcript)


if __name__ == "__main__":
    main()
