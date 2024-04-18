from transformers import BertTokenizer, BertModel
import torch
from scipy.spatial.distance import cosine
import numpy as np
import argparse

# Initialize tokenizer and model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def align_sentences(sentence1, sentence2):
    # Tokenize sentences and obtain model inputs
    inputs1 = tokenizer(sentence1, return_tensors='pt', add_special_tokens=False, max_length=512, truncation=True)
    inputs2 = tokenizer(sentence2, return_tensors='pt', add_special_tokens=False, max_length=512, truncation=True)

    # Obtain contextual embeddings for each token
    with torch.no_grad():
        outputs1 = model(**inputs1)
        outputs2 = model(**inputs2)

    # Only take the last layer hidden-state
    embeddings1 = outputs1.last_hidden_state.squeeze(0)  # Shape: (seq_length1, hidden_size)
    embeddings2 = outputs2.last_hidden_state.squeeze(0)  # Shape: (seq_length2, hidden_size)

    # Calculate cosine similarities
    similarity_matrix = torch.zeros((embeddings1.size(0), embeddings2.size(0)))

    for i, emb1 in enumerate(embeddings1):
        for j, emb2 in enumerate(embeddings2):
            similarity_matrix[i][j] = 1 - cosine(emb1, emb2)

    # Find alignments based on highest similarity score
    alignment_pairs = []
    for i in range(similarity_matrix.size(0)):
        j = similarity_matrix[i].argmax().item()
        alignment_pairs.append(f"{i}-{j}")

    # Concatenate alignment pairs to form the Pharaoh format
    pharaoh_format_alignment = " ".join(alignment_pairs)
    return pharaoh_format_alignment

def main(input_file):
    with open(input_file, 'r') as file:
        lines = file.readlines()

    with open('alignments.txt', 'w') as outfile:
        for line in lines:
            split_line = line.split("|||")
            print("{}//{}".format(split_line[0].strip(), split_line[1].strip()))
            # Example sentences
            sentence1 = split_line[0].strip()
            sentence2 = split_line[1].strip()
            if len(sentence1) == 0 or len(sentence2) == 0:
                continue
            pharaoh_format_alignment = align_sentences(sentence1, sentence2)
            outfile.write(pharaoh_format_alignment + "\n")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Align sentences from a text file.")
    parser.add_argument('input_file', type=str, help='Path to the file containing sentences to align.')
    args = parser.parse_args()

    main(args.input_file)