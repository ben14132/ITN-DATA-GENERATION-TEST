import argparse
import json

import utils


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

    #python3 ./model_train_inference/generate_train_test_file.py --json ./model_train_inference/env.json

    utils.generate_train_file(config['generate_train_test_file']['infile_dir_path'],
                              config['generate_train_test_file']['outfile_dir_path'])

    utils.generate_bitext_youtube_wenet(config['generate_train_test_file']['wenet_dir'],
                                        config['generate_train_test_file']['youtube_dir'],
                                        config['generate_train_test_file']['out_dir'])


if __name__ == "__main__":
    main()
