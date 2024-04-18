import sys
sys.path.append(r"D:\study\singaporeMasters\master_project\chng-pipeline")
#change line 185 to get just the transcript
import argparse
import shutil

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

# import data_crawl_preprocess.cal_wer as cal_wer
# import data_crawl_preprocess.cal_bleu as cal_bleu
import gen_speechbrain_transcript



FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

import logging
import logging.handlers

# create logger
logger = logging.getLogger('client')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
from pathlib import Path

# script_dir=os.path.dirname(os.path.realpath(__file__))
log_dir = "./log"
Path(log_dir).mkdir(parents=True, exist_ok=True)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logfh = logging.handlers.RotatingFileHandler(log_dir + "/" + 'client.log', maxBytes=10485760, backupCount=10)
logfh.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter(u'%(levelname)8s %(asctime)s %(message)s ')
logging._defaultFormatter = logging.Formatter(u"%(message)s")

# add formatter to ch
ch.setFormatter(formatter)
logfh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
logger.addHandler(logfh)


def rate_limited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)

    def decorate(func):
        lastTimeCalled = [0.0]

        def rate_limited_function(*args, **kargs):
            elapsed = time.perf_counter() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait > 0:
                time.sleep(leftToWait)
            ret = func(*args, **kargs)
            lastTimeCalled[0] = time.perf_counter()
            return ret

        return rate_limited_function

    return decorate


class MyClient(WebSocketClient):

    def __init__(self, mode, audiofile, url, protocols=None, extensions=None, heartbeat_freq=None, byterate=32000,
                 save_adaptation_state_filename=None, ssl_options=None, send_adaptation_state_filename=None, hotlist=0,
                 outdir=None):
        super(MyClient, self).__init__(url, protocols, extensions, heartbeat_freq)
        self.final_hyps = []
        self.outdir = outdir
        if self.outdir is None:
            self.txtfile = os.path.splitext(audiofile.name)[0] + ".txt"  # save txt result in same folder as input audio
        else:
            self.txtfile = self.outdir + "/" + os.path.splitext(os.path.basename(audiofile.name))[0] + ".txt"
        self.fileid = os.path.basename(os.path.splitext(audiofile.name)[0])
        self.audiofile = audiofile
        self.byterate = byterate
        self.final_hyp_queue = queue.Queue()
        self.save_adaptation_state_filename = save_adaptation_state_filename
        self.send_adaptation_state_filename = send_adaptation_state_filename
        self.hotlist = int(hotlist)

        self.ssl_options = ssl_options or {}

        if self.scheme == "wss":
            # Prevent check_hostname requires server_hostname (ref #187)
            if "cert_reqs" not in self.ssl_options:
                self.ssl_options["cert_reqs"] = ssl.CERT_NONE

        self.mode = mode
        self.audio = pyaudio.PyAudio()
        self.isStop = False

    # @rate_limited(4)
    @rate_limited(25)
    def send_data(self, data):
        self.send(data, binary=True)

    def opened(self):
        # logger.info("Socket opened! " + self.__str__())
        print("Byte rate", self.byterate)

        def send_data_to_ws():
            if self.send_adaptation_state_filename is not None:
                # logger.info("Sending adaptation state from %s" % self.send_adaptation_state_filename)
                try:
                    adaptation_state_props = json.load(open(self.send_adaptation_state_filename, "r"))
                    self.send(json.dumps(dict(adaptation_state=adaptation_state_props)))
                except:
                    e = sys.exc_info()[0]
                    # logger.info("Failed to send adaptation state: %s" % e)

            # logger.info("Start transcribing...")
            start_signal = json.dumps(
                {"signal": "start", "continuous_decoding": True, "nbest": 1, "sample_rate": self.byterate,
                 "hot_list": self.hotlist})
            print(start_signal)
            self.send(start_signal)
            if self.mode == 'stream':
                stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, input=True,
                                         frames_per_buffer=CHUNK)
                while not self.isStop:
                    data = stream.read(int(self.byterate / 8), exception_on_overflow=False)
                    self.send_data(data)  # send data

                stream.stop_stream()
                stream.close()
                self.audio.terminate()
            elif self.mode == 'file':

                with self.audiofile as audiostream:
                    for block in iter(lambda: audiostream.read(int(self.byterate / 4)), ""):
                        # 32000/4 = 8000 chunk -> server resample to 16khz
                        # 16000/4 = 4000 chunk -> server will not resample
                        # 640 *2 = 1280 chunk -> server wil not resample(simulate streaming for 16khz)
                        # 640 = 640 chunk ->
                        # for block in iter(lambda: audiostream.read(int(4000)), ""):
                        if len(block) == 0:
                            break
                        self.send_data(block)

            # logger.info("Audio sent, now sending EOS")
            self.send("EOS")

        t = threading.Thread(target=send_data_to_ws)
        t.start()

    def received_message(self, m):
        response = json.loads(str(m))
        # logger.info(response)
        if response['status'] == 0:
            if 'result' in response:
                trans = response['result']['hypotheses'][0]['transcript']
                if response['result']['final']:
                    # print >> sys.stderr, trans,
                    self.final_hyps.append(trans)
                    full_trans = " ".join(self.final_hyps)
                    start_seg = str(response['result']['hypotheses'][0]['segment-start'])
                    end_seg = str(response['result']['hypotheses'][0]['segment-end'])
                    print(self.fileid)

                    # save transcript
                    # default: same as wav dir or Given: defined by used
                    # output_sent = "{} {} {} {}\n".format(self.fileid, start_seg, end_seg, trans) (old code)
                    output_sent = "{}\n".format(trans) #remove everything except for trans to get just the transcript

                    with open(self.txtfile, 'a') as aw:
                        aw.writelines(output_sent)

                    with open(self.txtfile[:-4] + "_timestamp.txt", 'a') as word_f:
                        print(response['result']['hypotheses'][0])
                        word_timestamps = response['result']['hypotheses'][0]['word-alignment']
                        word_timestamps_processed = []
                        for word_stamp in word_timestamps:
                            if str(word_stamp['word']).startswith('▁'):
                                word_timestamps_processed.append(
                                    # [str(word_stamp['word']), str(word_stamp['start']), str(word_stamp['end'])])
                                    [str(word_stamp['word'])[1:].lower(), str(word_stamp['start']), str(word_stamp['end'])])
                            else:
                                word_timestamps_processed[-1][0] = word_timestamps_processed[-1][0] + str(word_stamp['word']).lower()
                                word_timestamps_processed[-1][2] = str(word_stamp['end'])
                        for word_stamp in word_timestamps_processed:
                            word_f.writelines(word_stamp[0] + ' ' + word_stamp[1] + ' ' + word_stamp[2] + '\n')

                    # print("\033[H\033[J") # clear console for better output
                    # logger.info('%s' % trans)
                else:
                    print_trans = trans
                    if len(print_trans) > 80:
                        print_trans = "... %s" % print_trans[-76:]

                    # print("\033[H\033[J") # clear console for better output
                    # logger.info('%s' % print_trans)
            if 'adaptation_state' in response:
                if self.save_adaptation_state_filename:
                    # logger.info("Saving adaptation state to %s" % self.save_adaptation_state_filename)
                    with open(self.save_adaptation_state_filename, "w") as f:
                        f.write(json.dumps(response['adaptation_state']))
        else:
            # logger.info("Received error from server (status %d)" % response['status'])
            if 'message' in response:
                logger.info("Error message: %s" % response['message'])

    def get_full_hyp(self, timeout=60):
        return self.final_hyp_queue.get(timeout)

    def closed(self, code, reason=None):
        # print "Websocket closed() called"
        # print >> sys.stderr
        self.final_hyp_queue.put(" ".join(self.final_hyps))


def main():
    parser = argparse.ArgumentParser(description='Command line client for kaldigstserver')
    parser.add_argument('-o', '--option', default="file", dest="mode",
                        help="Mode of transcribing: audio file or streaming")
    parser.add_argument('-u', '--uri', default="ws://localhost:8888/client/ws/speech", dest="uri",
                        help="Server websocket URI")
    parser.add_argument('-r', '--rate', default=32000, dest="rate", type=int,
                        help="Rate in bytes/sec at which audio should be sent to the server. NB! For raw 16-bit audio it must be 2*samplerate!")
    parser.add_argument('-t', '--token', default="", dest="token", help="User token")
    parser.add_argument('-m', '--model', default=None, dest="model", help="model in azure container")
    parser.add_argument('-hw', '--hotword', default=0, dest="hotword", type=int,
                        help="Toogle hotword usage. 0 means no hotword. 1 means hot1. Hotword file reside in Wenet2_2 dir")
    parser.add_argument('-gt', '--ground-truth', default=None, dest="ground_truth",
                        help="ground truth transcript file dir")
    parser.add_argument('-op', '--output', default="", dest="output", help="Output folder to store transcript")
    parser.add_argument('--save-adaptation-state', help="Save adaptation state to file")
    parser.add_argument('--send-adaptation-state', help="Send adaptation state from file")
    parser.add_argument('--content-type', default='',
                        help="Use the specified content type (empty by default, for raw files the default is  audio/x-raw, layout=(string)interleaved, rate=(int)<rate>, format=(string)S16LE, channels=(int)1")
    parser.add_argument('audiofile', nargs='?', help="Audio file to be sent to the server",
                        type=argparse.FileType('rb'), default=sys.stdin)
    args = parser.parse_args()


    wers = dict()
    bleus = dict()
    transcripts = dict()
    audio_file_name = os.path.basename(args.audiofile.name)[:-4]  # my_file

    if args.mode == 'file' or args.mode == 'stream':
        content_type = args.content_type
        if content_type == '' and args.audiofile.name.endswith(".raw") or args.mode == 'stream':
            content_type = "audio/x-raw, layout=(string)interleaved, rate=(int)%d, format=(string)S16LE, channels=(int)1" % (
                    args.rate / 2)

        outpath = os.path.splitext(args.audiofile.name)[0] + ".txt"
        ws = MyClient(args.mode, args.audiofile,
                      args.uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])) + '&%s' % (
                          urllib.parse.urlencode([("token", args.token)])) + '&%s' % (
                          urllib.parse.urlencode([("token", args.token)])) + '&%s' % (
                          urllib.parse.urlencode([("model", args.model)])), byterate=args.rate,
                      save_adaptation_state_filename=args.save_adaptation_state,
                      send_adaptation_state_filename=args.send_adaptation_state, hotlist=args.hotword,
                      outdir=args.output)

        ws.connect()
        result = ws.get_full_hyp()

        # logger.info("\n URL: " + str(
        #     args.uri + '?%s' % (urllib.parse.urlencode([("content-type", content_type)])) + '?%s' % (
        #         urllib.parse.urlencode([("token", args.token)]))) + "\n")
        # logger.info("\n------------------------\nFinal Result: \n")
        logger.info(result)
    else:
        print('\nTranscribe mode must be file or stream!\n')

    if args.ground_truth is not None and args.ground_truth != "":
        # audio_file_name = os.path.basename(args.audiofile.name)[:-4]  # my_file
        audio_file_path = os.path.join(args.ground_truth, audio_file_name + '.txt')
        ground_truth_list = []
        ground_truth = ''
        if os.path.exists(audio_file_path):
            with open(audio_file_path, 'r+') as f:
                lines = f.readlines()
                for line in lines:
                    ground_truth_list.append(line)
                    ground_truth = ' '.join(ground_truth_list)
        # wers['wenet'] = cal_wer.cal_wer_jiwerr(ground_truth, [('wenet', result)])[0][1]['wer']
        # bleus['wenet'] = cal_bleu.cal_BLEU_nltk(ground_truth, [('wenet', result)])[0][1]
        transcripts['wenet'] = result

        funs = ["asr-transformer-transformerlm-librispeech", "asr-crdnn-rnnlm-librispeech"]
        for fun in funs:
            transcripts[fun] = gen_speechbrain_transcript.gen_transcripts(args.audiofile.name, fun)
        funs.append('wenet')
        # logger.info(transcripts["asr-transformer-transformerlm-librispeech"])

        # commented this part out
        # for key in transcripts:
        #     wers[key] = cal_wer.cal_wer_jiwerr(ground_truth, [(key, transcripts[key])])[0][1]['wer']
        #     bleus[key] = cal_bleu.cal_BLEU_nltk(ground_truth, [(key, transcripts[key])])[0][1]

        # logger.info(transcripts)

    if args.output is None:
        args.output = './'
    if not os.path.exists(args.output):
        os.makedirs(args.output)
    # else:
    #     shutil.rmtree(args.output, ignore_errors=True)
    out_dir = args.output
    for key in transcripts:
        algo_out_dir = os.path.join(out_dir, key)
        if not os.path.exists(algo_out_dir):
            os.makedirs(algo_out_dir)
        algo_out_file = os.path.join(algo_out_dir, audio_file_name + '.txt')
        with open(algo_out_file, 'w+') as out_f:
            out_f.writelines('wer:' + str(wers[key]) + '\n')
            out_f.writelines('bleu:' + str(bleus[key]) + '\n')
            out_f.writelines(transcripts[key])


if __name__ == "__main__":
    main()

# wavpath port hotword expdir groundtruth
# bash gen_transcript_analyse_save.sh ./testdata/0927/wav 8016 0 ./exp/0927 ./testdata/0927
