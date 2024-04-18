import argparse
import json
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()

    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)

    input_dir = config["aggregration"]["input_dir"]
    output_file = config["aggregration"]["output_file"]

    out_fp = open(output_file, 'w+')
    for file_name in os.listdir(input_dir):
        file_path = os.path.join(input_dir, file_name)
        with open(file_path, 'r+') as in_fp:
            lines = in_fp.readlines()
            for line in lines:
                out_fp.write(line + '\n')

    out_fp.close()
    pass


if __name__=="__main__":
    main()