"""
Author: Suthakar Shiny Gladdys
Last Modified by : Charangan Vasantharajan
Date: 05/04/2022 
Description: Segment sentences with times
Args:
    Inputs
        file_path (str): string to input file path [Required]
"""

import os
import regex as re
import pandas as pd
import spacy
# from deepsegment import DeepSegment
import unidecode
from num2words import num2words
import argparse
import json
import glob

# Map YouTube words to CMU words
yt2kaldi_word =  {
    "mdm": "madam", "mdm.": "madam", # Salutations
    "ms": "miss", "ms.": "miss",
    "mrs": "missus", "mrs.": "missus",
    "dr": "doctor", "dr.": "doctor",
    "mr": "mister", "mr.": "mister",
    "%": "percent", "#": "hashtag ", "&": "and", "$": "dollar", # Symbols
    "[music]": "", "[applause]": "", # Fillers
    "[laughter]": "", "[musik]": ""
}


def text_normalization(sentence):
    sentence = sentence.replace('-', 'X') # Handle hyphen, e.g. two-hour
    sentence = sentence.split(' ')

    # Convert to lower case
    sentence = [t.lower() for t in sentence]

    # Align sentence with CMU words
    check_keys = yt2kaldi_word.keys()
    sentence = [(yt2kaldi_word[t] if t in check_keys else t) for t in sentence]

    # Normalize numbers
    # for i, word in enumerate(sentence):
    #     sentence[i] = re.sub(
    #         r"(\d+)", lambda x: num2words(int(x.group(0))), word)

    # Strip accents from characters
    sentence = [unidecode.unidecode(t) for t in sentence]

    return ' '.join(sentence)


def sentence_segmentation(df):

    first_word_st = df.iloc[0,0].split(' -->')[0] # get start time of first word
    df = df.iloc[1::2] # remove redundant lines
    df = df.reset_index(drop=True)

    # split words together with their end times
    df['times'] = df['times'].str.split(' ')
    s = df.apply(lambda x: pd.Series(x['times']), axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'times'
    df = df.drop('times', axis=1).join(s)
    df = df[df['times'].str.contains("<") == True]
    df = df.reset_index(drop=True)
    df['times_2'] = df['times'].str.split('<')
    df.loc[:, 'word'] = df.times_2.map(lambda x: x[0])
    df.loc[:, 'end_time'] = '<' + df.times_2.map(lambda x: x[1])

    # get start time of each word
    df['start_time'] = df['end_time'].shift(1)
    df['start_time'].iloc[0] = '<' + first_word_st + '>'
    df = df[['start_time', 'end_time', 'word']]

    # Initialize start_idx to 0
    start_idx = 0

    # Lists to hold the start and end index of each word
    start_indices = []
    end_indices = []

    # Loop through each word and calculate start_idx and end_idx
    for word in df['word']:
        # The end index is the start plus the length of the word
        end_idx = start_idx + len(word)

        # Append the indices to the lists
        start_indices.append(start_idx)
        end_indices.append(end_idx)

        # Update start_idx for the next word to be the end index plus 1 (assuming a space)
        start_idx = end_idx + 1

    # Add the start and end indices to the DataFrame
    df['start_idx'] = start_indices
    df['end_idx'] = end_indices
    # apply segmentation
    full_text = ' '.join(df["word"]) # concatenate all the words
    # segmenter = DeepSegment('en')
    segmenter = spacy.load('en_core_web_sm')
    doc = segmenter(full_text)

    # sentence = segmenter(full_text)
    # sentence_list = list(sentence.sents)
    # # sentence_list = segmenter.segment_long(full_text)
    # df2 = pd.DataFrame(columns=['sentence'])
    # df2['sentence'] = sentence_list
    # df2.index += 1 # index serves as sentence number
    # df3 = pd.DataFrame(columns=['word_list'])
    # df3['word_list'] = df2['sentence'].str.split(' ')
    # s2 = df3.apply(lambda x: pd.Series(x['word_list']), axis=1).stack().reset_index(level=1, drop=True)
    # s2.name = 'word_2'
    # df3 = df3.drop('word_list', axis=1).join(s2)
    # df3['sentence_number'] = df3.index
    # df3 = df3.reset_index(drop=True)
    # df3.index += 1
    #
    # # match words with their sentence numbers
    # df.index += 1
    # df4 = pd.merge(df, df3, left_index=True, right_index=True)
    # df4 = df4.drop('word_2', axis=1)
    # df5 = df4.groupby('sentence_number').first() # find first and last words of each sentence
    # df6 = df4.groupby('sentence_number').last()
    # df5 = df5.drop(['word', 'end_time'], axis=1) # get start and end times of each sentence
    # df6 = df6.drop(['word', 'start_time'], axis=1)
    # df5 = pd.merge(df5, df6, left_index=True, right_index=True)
    # df2 = pd.merge(df2, df5, left_index=True, right_index=True)

    # Create a DataFrame to hold sentences and their start and end times
    sentences_df = pd.DataFrame(columns=['sentence', 'start_time', 'end_time'])

    # Initialize variables to hold the start and end indices of words in sentences
    start_idx = 0  # Start index of the first word in a sentence
    end_idx = 0  # End index of the last word in a sentence

    # Loop through the sentences in the doc
    for sent in doc.sents:
        # The text of the sentence
        sentence_text = sent.text.strip()

        # Find the first and last tokens in the sentence that are not spaces
        first_token = next(token for token in sent if not token.is_space)
        last_token = next(token for token in reversed(sent) if not token.is_space)

        # The start index of the first word in the current sentence
        start_idx = first_token.idx
        # The end index of the last word in the current sentence
        end_idx = last_token.idx + len(last_token)

        # The start time for the current sentence
        sentence_start_time = df.iloc[df['start_idx'].searchsorted(start_idx, side='left')]['start_time']
        # The end time for the current sentence
        sentence_end_time = df.iloc[df['end_idx'].searchsorted(end_idx, side='right') - 1]['end_time']

        # Append the sentence data to the sentences_df DataFrame
        sentences_df = sentences_df._append({
            'sentence': sentence_text,
            'start_time': sentence_start_time,
            'end_time': sentence_end_time
        }, ignore_index=True)


    # text normalization
    # for index, row in df2.iterrows():
    #     row.sentence = text_normalization(str(row.sentence))

    for index, row in sentences_df.iterrows():
        row.sentence = text_normalization(str(row.sentence))

    # return df2
    return sentences_df

def segment_file(config):
    file_path = config["sentence_segmentation_with_times"]["path"]
    os.chdir(os.path.dirname(file_path))
    new_file_path = os.path.join(os.getcwd(), 'segmented_text_with_times' + '.txt')

    new_file = open(new_file_path, 'a')
    test_df = pd.read_csv(file_path, names=['times'], skiprows=3)
    for index, row in sentence_segmentation(test_df).iterrows():
        lineToWrite = row.start_time + ' ' + row.end_time + '    ' + row.sentence + '\n'
        new_file.write(lineToWrite)
    new_file.close()


def segment_folder(config):
    folder_path = config["sentence_segmentation_with_times"]["path"]
    os.chdir(folder_path)
    new_folder_path = os.path.join(
        os.path.dirname(os.getcwd()), 'segmented_text_with_times')

    if(not os.path.exists(new_folder_path)):
        os.makedirs(new_folder_path)

    for file in os.listdir():
        if file.endswith(".vtt"):
            file_path = f"{folder_path}/{file}"

            os.chdir(os.path.dirname(file_path))
            new_file_path = os.path.join(new_folder_path, file)

            new_file = open(new_file_path, 'w+')
            test_df = pd.read_csv(file_path, names=['times'], skiprows=3)
            for index, row in sentence_segmentation(test_df).iterrows():
                lineToWrite = str(row.start_time) + ' ' + str(row.end_time) + '    ' + str(row.sentence) + '\n' #changed all classes to str here
                new_file.write(lineToWrite)
            new_file.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    args = parser.parse_args()
    with open(args.json, "r") as j_obj:
        config = json.load(j_obj)

    if(config["sentence_segmentation_with_times"]["input_type"] == "file"):
        segment_file(config)
    else:
        segment_folder(config)


if __name__ == "__main__":
    main()
