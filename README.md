# ITN-data-generation

[//]: # (generate ITN dataset)

This is the repo for "Adopting Neural Translation Model in Data Generation for Inverse Text Normalization"

This project aims for developing a word level dataset generation pipeline for Inverse Text Normalization (ITN) task. 

The following shows the spoken form accuracy of the generated dataset by applying different word alignment strategy into the pipeline.

[//]: # (eg：![image]&#40;https://raw.githubusercontent.com/lulushen/SwiftNotes/master/image/1.png&#41;)

| method                                                       | spoken form accuracy |
|:-------------------------------------------------------------|---------------------:|
| [FastAlign](https://github.com/clab/fast_align)              |                 77.0 |
| [GIZA++](http://www2.statmt.org/moses/giza/GIZA++.html)      |                 83.6 | 
| [Mask Align](https://github.com/THUNLP-MT/Mask-Align)        |                 85.2 | 
| [Awesome-Align](https://github.com/neulab/awesome-align)     |                 85.2 |  
| **Ours**                                                     |             **88.5** |

## Requirements
Two environments are needed. One for data crawling and cleaning, the other for word level alignment.
Establish the crawling and cleaning environment through requirements/requirements_crawling.txt.
Establish the world level alignment environment through following command:
```
pip install --user --editable ./Cross-Align/
```

## Setps for generation
# step 1: data crawling and cleaning
In this step, the pipeline gathers the audios and transcripts of certain youtuber from Youtube, then clean the transcripts and do segmentation.
```
./crawl_youtube/youtube_crawler.sh 7 "<out_base_dir>" "<youtuber name>"
```
This step employs [Deepsegment](https://github.com/notAI-tech/deepsegment) as segmentor. 
If need to switch to better segmentor, please refer to ./get_vtt_and_clean/sentence_segmentation_with_times.py and change to your segmentor on line 80.

# step 2: generate spoken form transcript
In this step, the audios are divided in sentence level and generate sentence level transcript using WeNet ASR. Note to setup a WeNet ASR server before running. 
First, generate the segmented wav files:
```
./generate_separated_wav_transcript.sh "D:/study/singaporeMasters/master_project/term2/repository/to_submit/data" "Chris @HoneyMoneySG"
```
Then, run script to get ASR result from server.
```
./get_wenet_output/gen_transcript_analyse_save.sh "<wav_dir>" <server_port> <if_using_hot_words> "<output_dir>" "<Optional:ground_truth_dir>"
```
If need to connect to a local WenNet, please refer to ./get_wenet_output/test_local_wenet.py
The pipeline also supports other model on speechbrain. If need to add model, please refer to ./get_wenet_output/gen_transcript_analyse_save.py line 93 and ./get_wenet_output/generate_separated_wav_transcript.py line 303. 
speechbrain models are available when "<Optional:ground_truth_dir>" is provided.

# step 3: train model and inference
[Text Normalization for English, Russian and Polish](https://www.kaggle.com/datasets/richardwilliamsproat/text-normalization-for-english-russian-and-polish) released by Google is used to train and test the model.
First do data pre-processing. Use generate_train_file() in utils.py to generate required format of Cross-Align along with ground truth alignment. 
Then follow Cross-Align's instruction to train the model and inference. 
Use utils.generate_bitext_youtube_wenet() to generate input from fetched data and utils.generate_alignment_tsv to generate dataset in format same to Google text normalization dataset.
At last, use generate_alignment_tsv(), post_process(), and post_process_2() in utils.py to reformat and clean the outputs.
```
./model_train_inference/generate_train_test_file.py --json ./model_train_inference/env.json
```
```
./model_train_inference/generate_dataset.py --json ./model_train_inference/env.json
```
Remember to modify parameters in env.json before running the script.


