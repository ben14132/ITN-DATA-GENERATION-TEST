import os, argparse, glob

parser = argparse.ArgumentParser(description='Get Video ids in dir to process for VTT')

parser.add_argument("--path",
			default = ".",
			metavar = 'path',
			help = 'path for input transcript dir to output video_ids dir')

def get_vid_ids(in_transcripts, out_vid_ids):
    transcript_files = os.listdir(in_transcripts)
    idxs = [os.path.splitext(f)[0] for f in transcript_files]
    if not os.path.exists(out_vid_ids):
        os.mkdir(out_vid_ids)
    out_vid_ids_file = os.path.join(out_vid_ids, 'video_ids.txt')
    with open(out_vid_ids_file, "w") as f:
        for idx in idxs:
            f.write(idx + "\n")

if __name__=="__main__":
    args = parser.parse_args()
    path = args.path
    in_transcripts = os.path.join(path, 'transcripts')
    out_vid_ids = os.path.join(path, 'video_ids')
    get_vid_ids(in_transcripts, out_vid_ids)