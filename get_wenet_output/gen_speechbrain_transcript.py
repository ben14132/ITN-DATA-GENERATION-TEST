# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import os
import shutil

from pydub import audio_segment
from speechbrain.pretrained import EncoderDecoderASR

# 140M -> 78min -> allocate 36G
# I have 8G cuda, so divide to 6 parts // not feasible on 8G gpu, so run on 32G memory cpu, 720s wav may take 20+G
# currently test result is 90s okay

max_wav_length = 20 * 1000


def gen_transcripts_and_save(input_dir_path, output_dir_path, model):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    asr_model = None
    if model == "asr-crdnn-rnnlm-librispeech":
        asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech",
                                                   savedir="pretrained_models/asr-crdnn-rnnlm-librispeech",
                                                   run_opts={"device": "cuda"})
    elif model == "asr-transformer-transformerlm-librispeech":
        asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-transformer-transformerlm-librispeech",
                                                   savedir="pretrained_models/asr-transformer-transformerlm-librispeech",
                                                   run_opts={"device": "cuda"})
    if asr_model is None:
        raise Exception("no model")
    # asr_model.transcribe_file("speechbrain/asr-transformer-transformerlm-librispeech/example.wav")
    print("model=" + model)
    os.getcwd()
    source_folder = os.path.abspath(input_dir_path)
    target_folder = os.path.abspath(output_dir_path)
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
    # os.chdir(input_dir)
    # input_cwd = os.getcwd()
    for file in os.listdir(input_dir_path):
        if file.endswith('.wav'):
            print('doing with ' + file)
            file_path = os.path.join(source_folder, file)

            wav = audio_segment.AudioSegment.from_wav(file_path)
            duration = wav.duration_seconds * 1000

            transcripts = []

            if duration <= max_wav_length:
                print('do with no slide')
                transcript = asr_model.transcribe_file(file_path)
                transcripts.append(transcript.lower())
                print(transcript)
            else:
                segment_num = duration // max_wav_length + 1
                segment_length = duration // segment_num + 1
                print('slide into ' + str(segment_num) + ' parts')
                new_target_folder = os.path.join(target_folder, file[:-4])
                if not os.path.exists(new_target_folder):
                    os.makedirs(new_target_folder)
                else:
                    shutil.rmtree(new_target_folder)
                    os.makedirs(new_target_folder)
                begin = 0
                end = begin + segment_length
                for i in range(int(segment_num)):
                    cut_wav = wav[begin:end]
                    new_file_path = os.path.join(new_target_folder, file[:-4] + '-' + str(i).zfill(4) + '.wav')
                    cut_wav.export(new_file_path, format='wav')
                    begin = end + 1
                    end = begin + segment_length
                    if end > duration:
                        end = duration
                for segment_file in os.listdir(new_target_folder):
                    if segment_file.endswith('.wav'):
                        segment_file_path = os.path.join(new_target_folder, segment_file)
                        transcript = asr_model.transcribe_file(segment_file_path)
                        transcripts.append(transcript.lower())
                        print(segment_file + ' finished')
                        print(transcript)
            print(file + ' complete')
            with open(os.path.join(target_folder, file[:-4] + '-' + model) + '.txt', 'w+') as out_file:
                out_file.write(' \n'.join(transcripts))

    print('done')

# generate transcript using speechbrain model
def gen_transcripts(input_file_path, model):
    # Use a breakpoint in the code line below to debug your script.
    # print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.
    asr_model = None
    if model == "asr-crdnn-rnnlm-librispeech":
        asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-crdnn-rnnlm-librispeech",
                                                   savedir="pretrained_models/asr-crdnn-rnnlm-librispeech",
                                                   run_opts={"device": "cuda"})
    elif model == "asr-transformer-transformerlm-librispeech":
        asr_model = EncoderDecoderASR.from_hparams(source="speechbrain/asr-transformer-transformerlm-librispeech",
                                                   savedir="pretrained_models/asr-transformer-transformerlm-librispeech",
                                                   run_opts={"device": "cuda"})
    if asr_model is None:
        raise Exception("no model")
    # asr_model.transcribe_file("speechbrain/asr-transformer-transformerlm-librispeech/example.wav")
    print("model=" + model)
    os.getcwd()
    file = os.path.abspath(input_file_path)
    transcripts = []
    if file.endswith('.wav'):
        print('doing with ' + file)
        file_path = file

        wav = audio_segment.AudioSegment.from_wav(file_path)
        duration = wav.duration_seconds * 1000

        if duration <= max_wav_length:
            print('do with no slide')
            transcript = asr_model.transcribe_file(file_path)
            transcripts.append(transcript.lower())
            print(transcript)
        else:
            segment_num = duration // max_wav_length + 1
            segment_length = duration // segment_num + 1
            print('slide into ' + str(segment_num) + ' parts')
            new_source_folder = os.path.join('./', file[:-4])
            if not os.path.exists(new_source_folder):
                os.makedirs(new_source_folder)
            else:
                shutil.rmtree(new_source_folder)
                os.makedirs(new_source_folder)
            begin = 0
            end = begin + segment_length
            for i in range(int(segment_num)):
                cut_wav = wav[begin:end]
                new_file_path = os.path.join(new_source_folder, file[:-4] + '-' + str(i).zfill(4) + '.wav')
                cut_wav.export(new_file_path, format='wav')
                begin = end + 1
                end = begin + segment_length
                if end > duration:
                    end = duration
            for segment_file in os.listdir(new_source_folder):
                if segment_file.endswith('.wav'):
                    segment_file_path = os.path.join(new_source_folder, segment_file)
                    transcript = asr_model.transcribe_file(segment_file_path)
                    transcripts.append(transcript.lower())
                    print(segment_file + ' finished')
                    print(transcript)
        print(file + ' complete')
    return ' '.join(transcripts)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # main3()

    input_dir = 'JoshTanTheAstuteParent/0927/wav'
    output_dir = 'JoshTanTheAstuteParent/0927/'
    # input_dir = r'D:\study\singaporeMasters\master project\git\score-wer-online\testdata\imda-part2-sm\wav\\'
    # output_dir = r'D:\study\singaporeMasters\master project\chng-pipeline\JoshTanTheAstuteParent\exp-imdapart2sm-nohw\\'
    funs = ["asr-transformer-transformerlm-librispeech", "asr-crdnn-rnnlm-librispeech"]
    for fun in funs:
        gen_transcripts_and_save(input_dir, output_dir + fun, fun)
    print(os.getcwd())

    # main2()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
