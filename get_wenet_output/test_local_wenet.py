import argparse
import json
import os
import shutil
import sys
import torch
import wenetruntime as wenet


def main(args):
    for wav_sub_folder in os.listdir(args.wav_folder):
        wav_sub_folder_path = os.path.join(args.wav_folder, wav_sub_folder)
        wav_sub_folder_path = os.path.join(wav_sub_folder_path, 'wav')
        transcript_sub_folder_path = os.path.join(args.output_folder, wav_sub_folder)
        if not os.path.exists(transcript_sub_folder_path):
            os.mkdir(transcript_sub_folder_path)
        else:
            shutil.rmtree(transcript_sub_folder_path, ignore_errors=True)
            os.mkdir(transcript_sub_folder_path)

        for wav_file in os.listdir(wav_sub_folder_path):
            try:
                print(wav_file)
                wav_file_path = os.path.join(wav_sub_folder_path, wav_file)
                decoder = wenet.Decoder(lang='en', enable_timestamp=True)
                ans = decoder.decode_wav(wav_file_path)
                # print(ans)

                response = json.loads(str(ans))
                result_sentence = response['nbest'][0]['sentence']
                word_timestamps = response['nbest'][0]['word_pieces']
                word_timestamps_processed = []
                for word_stamp in word_timestamps:
                    if str(word_stamp['word']).startswith('▁'):
                        word_timestamps_processed.append(
                            # [str(word_stamp['word']), str(word_stamp['start']), str(word_stamp['end'])])
                            [str(word_stamp['word'])[1:].lower(), str(word_stamp['start']), str(word_stamp['end'])])
                    else:
                        word_timestamps_processed[-1][0] = word_timestamps_processed[-1][0] + str(word_stamp['word']).lower()
                        word_timestamps_processed[-1][2] = str(word_stamp['end'])

                # for word_stamp in word_timestamps_processed:
                #     word_f.writelines(word_stamp[0] + ' ' + word_stamp[1] + ' ' + word_stamp[2] + '\n')
                with open(os.path.join(transcript_sub_folder_path, wav_file[:-4] + '_transcript.txt'), 'w+') as transcript_f:
                    transcript_f.write(result_sentence)
                with open(os.path.join(transcript_sub_folder_path, wav_file[:-4] + '_timestamp.txt'), 'w+') as timestamp_f:
                    for word_stamp in word_timestamps_processed:
                        timestamp_f.writelines(word_stamp[0] + ' ' + word_stamp[1] + ' ' + word_stamp[2] + '\n')
            except Exception as e:
                print(e)


if __name__=="__main__":
    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-wav-folder', '-w', default=r'D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\segmented_wav', dest='wav_folder',
                        help="input wav files' dir")
    parser.add_argument('-output-folder', '-o', default=r'D:\study\singaporeMasters\master_project\term2\data\youtube_crawler\Chris@HoneyMoneySG\wenet_transcript', dest='output_folder',
                        help="output folder of transcripts")
    args = parser.parse_args()

    main(args)

