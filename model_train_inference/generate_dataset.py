import argparse
import json
import os

import utils


def main():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument("--json", required=True)

    args = parser.parse_args()

    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)

    utils.generate_alignment_tsv(config['generate_dataset']['data_dir_path'], config['generate_dataset']['test_data'], config['generate_dataset']['out_alignment'], config['generate_dataset']['output_name'])
    output_file_path = os.path.join(config['generate_dataset']['data_dir_path'], config['generate_dataset']['output_name'])
    utils.post_process(config['generate_dataset']['data_dir_path'], output_file_path, config['generate_dataset']['output_name'] + "_post1")
    utils.post_process_2(config['generate_dataset']['data_dir_path'], output_file_path, config['generate_dataset']['output_name'] + "_post2")

if __name__ == "__main__":
    main()

    #python3 ./model_train_inference/generate_dataset.py --json ./model_train_inference/env.json
