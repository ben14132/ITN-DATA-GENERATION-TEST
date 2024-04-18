"""
Author: Lim Zhi Hao
Data Created: 01/05/2021
Modified by : Charangan Vasantharajan
Date: 05/04/2022
Description: 	This script is used to find/filter/fetch transcripts 
				from youtube videos based on a certain language

				The original use-case is to crawl additional indonesian
				news to train our indonesian ASR

				OUSTANDING ISSUES, youtube_transcript_api does not fetch
				correct time boundaries for their automated captions. This
				is an issue with their API. Work around is to find another
				python library that can fetch transcripts with correct time
				boundaries. Meanwhile, I just realign the transcript to the
				best of my judgement.
Args:
    Inputs
		search-terms (list): Search terms for youtube videos
		language (list): Language id of transcription to be downloaded
		num-pages (int): Number of search result pages to crawl from
		min-duration (int): Minimum duration of video, in seconds
		sample-rate (int): Sampling rate of output wav
		wav-dir (str): Directory for wav files
		mp4-dir (str): Directory for mp4 files
		transcripts-dir (str): directory for transcription files
		verbose (option): Set verbosity level
		to-wav (option): Convert downloaded mp4 audio to wav
		as-video (option): Download video instead of audio
		channel-only (option): Search by channel name only
		audio-only (option): Search by channel name only
		use-manual (option): Fetch manual transcription only
		id-only (option): Fetch video ids only
		ids-dir (str): directory for transcription files
"""

#./crawl_youtube/youtube_crawler.sh 7 "/Users/bennettlee/Desktop/ITN Pipeline" "Chris @HoneyMoneySG"

import os, argparse
from youtubesearchpython import *
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from pydub import AudioSegment
import re


# -------------------------------- Utility Functions -------------------------------------- #


def folders_check(dir1,dir2):
	'''
	Check if there are paired transcripts+audio

	'''

	f1 = [os.path.splitext(f)[0] for f in os.listdir(dir1)]
	f2 = [os.path.splitext(f)[0] for f in os.listdir(dir2)]
	assert len(f1) == len(f2)

	f0 = list(set(f1).intersection(set(f2)))

	return len(f0) == len(f1)


def check_dir(dir2chk,verbose=False):
	print(dir2chk)
	if not os.path.isdir(dir2chk):
		if verbose:
			print('Making directory:',dir2chk)
		os.makedirs(dir2chk)
	else:
		if verbose:
			print('Directory',dir2chk,'exists, moving on')


def get_duration(duration_string):
	'''
	Return duration of video in seconds

	Input: duration_string (FMT is %H:%M:%S)

	'''

	duration = [int(i) for i in duration_string.split(':')]
	duration.reverse()

	return sum([d*(60**i) for i,d in enumerate(duration)])



# -------------------------------- Helper Functions --------------------------------------- #


def parse_search_terms(search_terms):

	''' Parse search strings into proper format'''

	return [term.replace('_',' ') for term in search_terms]



def download_audio(video_id, outdir, as_video=False):

	'''
	Given video id, download the audio only from youtube in mp4

	'''

	link = 'https://www.youtube.com/watch?v={}'.format(video_id)

	yt = YouTube(link)
	if not as_video:
		audio_stream = yt.streams.filter(only_audio=True)
	else:
		audio_stream = yt.streams.filter()

	outfile = audio_stream[0].download()

	outname,ext = os.path.splitext(outfile)
	newfile = os.path.join(outdir, video_id+ext)

	# Rename default name by pytube
	os.rename(outfile,newfile)



def search_links(search_str, num_pages=10, min_duration = 1200, verbose=False, channel_only=False):

	'''
	Search youtube with <search_str>
	Fetch only top <num_pages> of links
	Filter away based on duration greater than <min_duration>

	'''

	print('Searching youtube for: {}'.format(search_str))

	# Search youtube, either by channels or videos
	search = VideosSearch(search_str)

	all_results = []
	for page in range(num_pages):
		if verbose:
			print('Fetching results from page {}'.format(page), end='\r')

		# Fetch results or filter based on channels first
		if channel_only:
			results = [(D['duration'], D['link']) for D in search.result()['result'] if search_str in D['channel']['name']]
		else:
			results = [(D['duration'], D['link']) for D in search.result()['result']]


		# Convert string duration into float (in seconds) and filter based on duration
		results = [(get_duration(dur), link) for dur, link in results if dur is not None]
		filter_results = [[dur, link] for dur,link in results if dur >= min_duration]
		all_results += filter_results

		try:
			# Try to go to the next page of search results
			search.next()
		except Exception:
			# If cannot, no more pages left, break
			if verbose:
				print('No more search results for page {} onwards'.format(page))
			break

	num_links = len(all_results)
	print('Found {} links with duration longer than {}s'.format(num_links, min_duration))

	# Return sorted results
	all_results.sort()
	return all_results



def fix_transcript(transcript):

	'''
	There is some issue with the sentence boundaries when
	using YouTubeTranscriptApi. This function is to correct
	the boundaries to the best of my judgement

	'''

	# Extract text, start time, and duration of each segment
	text,start,duration = zip(*[list(D.values()) for D in transcript])

	# Used this line to offset for the start/end times
	times = list(start)+[duration[-1]+start[-1]]

	# Reassemble using the newly offset start/end times
	fix_transcript = []
	for i,t in enumerate(text):
		D = {}
		D['text'] = text[i]
		D['start'] = times[i]
		D['duration'] = times[i+1]-D['start']
		fix_transcript.append(D)

	return fix_transcript





def fetch_transcript(video_id, language, use_manual=True, auto_ok=True):

	''' Choose type of transcription to return  '''

	transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

	# If only scrap for manual transcription
	if use_manual:
		# Try to fetch manual transcription
		transcript = None
		try:
			transcript = transcript_list.find_manually_created_transcript(language)
		except Exception as e:
			print(video_id + " has no manual transcript")

		if transcript is None and auto_ok:
			# If no manual is available, force to use auto generated
			transcript = transcript_list.find_generated_transcript(language)

		return fix_transcript(transcript.fetch())

	else:
		transcript = YouTubeTranscriptApi.get_transcript(video_id,languages=language)
		return fix_transcript(transcript)



def get_transcript(youtube_links, language=['id'], verbose=False, use_manual=True):

	'''
	This function will attempt to fetch the auto captions (if available)
	The auto captions fetched will be based on the languages provided

	'''

	langs = ' '.join(language)
	num_links = len(youtube_links)
	if use_manual:
		t_type = 'manual'
	else:
		t_type = 'auto'

	print('Attempting to fetch {} transcripts for {} links'.format(t_type, num_links))

	transcripts = {}
	for i, (duration, link) in enumerate(youtube_links):
		if verbose:
			print('Fetching {} out of {} {} transcription'.format(i,num_links,langs), end='\r')

		# Get video id from link
		video_id = link.rsplit('=')[-1]

		try:
			# Attempt to fetch transcription if available for language(s)
			# most videos doesn't have manual transcripts, so just set auto_ok=true (originally false but useless \
			# because use_manual is always false)
			transcript = fetch_transcript(video_id, language, use_manual=use_manual, auto_ok=True)

			# NOTE: from above, this part "fixes" the time boundaries of transcription
			transcripts[video_id] = transcript
			if verbose:
				print('Successfully fetched transcription for '.format(link), end='\r')

		except Exception:
			if verbose:
				print('No trancription available for {}'.format(video_id))

	num_transcripts = len(transcripts)

	print('Number of videos with transcripts: {} out of {}'.format(num_transcripts, num_links))
	return transcripts




def write2file(transcript,outfile):

	'''
	Write list of dictionaries to text file

	'''

	writeline = lambda s,e,t: '{:.2f} {:.2f}\t{}\n'.format(s,e,t)
	with open(outfile,'w', encoding="utf-8") as F:
		module = re.compile(r'\[[a-zA-Z]*?\]')

		for i,line in enumerate(transcript):
			text = line['text']
			text = text.replace(u'\xa0', '')
			text = text.replace(u'\n', ' ')
			text = text.replace(u'\r', ' ')
			text = text.replace(u'\"', ' ')
			text = re.sub(module, '', text)
			start = line['start']
			duration = line['duration']
			end = start+duration
			F.write(writeline(start, end, text))


def save_transcripts(transcripts, outdir, verbose=False):

	num_transcripts = len(transcripts)
	print('Writing {} transcripts to {}'.format(num_transcripts, outdir))
	for video_id, transcript in transcripts.items():
		outfile = os.path.join(outdir,video_id+'.txt')
		if verbose:
			print('Writing {}'.format(outfile), end='\r')

		write2file(transcript, outfile)

		if verbose:
			print('Done', end='\r')

	print('Done')



# -------------------------------- Main Functions ----------------------------------------- #

def find_filter_fetch_transcripts(search_str, outdir,
				language = ['id'],
				num_pages = 100,
				min_duration = 100,
				channel_only = False,
				verbose = False,
				use_manual = False):

	'''
	Main function to find/filter/fetch transcripts

	The transcripts will be saved to outdir as <video_id>.txt
	In the format: <start-time> <end-time> <text> PER LINE

	Use the function download_audio_fetched() to read the
	transcripts directory and download the audio only in mp4

	Use the function convert2wav() to convert mp4files to wavfiles

	'''

	# Search and filter results
	long_links = search_links(search_str, num_pages, min_duration, verbose, channel_only)

	# Attempt to fetch transcripts
	transcripts = get_transcript(long_links, language, verbose, use_manual)

	# Save the transcripts to text format in outdir
	save_transcripts(transcripts, outdir, verbose)


def download_video_ids(video_ids, outdir, as_video):

	listlen = len(video_ids)
	# Try to download audio files
	error_logs = []
	for i, video_id in enumerate(video_ids):
		print('Downloading audio from {}'.format(video_id))
		try:
			download_audio(video_id, outdir, as_video)
		except Exception:
			error_log = 'Error download audio from: {}'.format(video_id)
			error_logs.append(error_log)
			print(error_log)
		print('Success, completed {} out of {}'.format(i+1, listlen))

	return error_logs


def download_audio_fetched(transcript_dir, outdir, as_video = False):

	video_ids = [t.split('.')[0] for t in os.listdir(transcript_dir)]
	num_transcripts = len(video_ids)

	error_logs = download_video_ids(video_ids, outdir, as_video)

	# If error occured in downloading the mp4 audio from youtube
	# We have to remove the transcipts accordingly
	if len(error_logs) > 0:
		print('Completed with some errors:')
		# Cleanup by removing extra transcription files
		for error in error_logs:
			video_id = error.split(': ')[-1]
			transcript_file = os.path.join(transcript_dir,video_id+'.txt')
			os.remove(transcript_file)
			print('Removing {}'.format(transcript_file))
	else:
		print(f'Successfully downloaded all {num_transcripts} audio with no errors')


def clean_up():

	''' Remove undeleted mp4files from working directory'''

	curr_path = os.getcwd()
	leftovers = [f for f in os.listdir(curr_path) if '.mp4' in f]

	for leftover in leftovers:
		os.remove(os.path.join(curr_path,leftover))



def convertmp4(mp4files, wavdir, sample_rate):

	get_name = lambda s: os.path.splitext(os.path.split(s)[-1])[0]
	numfiles = len(mp4files)

	# Atttempt to convert mp4 into wav
	error_logs = []
	for i,mp4file in enumerate(mp4files):
		print('Converting {} to wav'.format(mp4file))
		wavfile = os.path.join(wavdir,get_name(mp4file)+'.wav')
		try:
			mp4_version = AudioSegment.from_file(mp4file, "mp4").set_frame_rate(sample_rate)
			mp4_version.export(wavfile, format="wav", parameters=["-ac", "1"])
		except Exception:
			error_log = 'Error convertingaudio: {}'.format(mp4file)
			error_logs.append(error_log)
			print(error_log)

		print('Completed {} out of {}'.format(i+1,numfiles))

	return error_logs

def convert2wav(mp4dir, wavdir, transcript_dir, sample_rate=16000):
	mp4files = [os.path.join(mp4dir,f) for f in os.listdir(mp4dir) if '.mp4' in f]
	numfiles = len(mp4files)
	print('Detected {} mp4 files'.format(numfiles))

	error_logs = convertmp4(mp4files, wavdir, sample_rate)
	get_name = lambda s: os.path.splitext(os.path.split(s)[-1])[0]

	# If error occured in conversion from mp4 to wav
	# We have to remove the mp4 and transcipts accordingly
	if len(error_logs) > 0:
		print('Completed with some errors:')
		# Cleanup by removing extra transcription files
		for error in error_logs:
			mp4file = error.split(': ')[-1]
			video_id = get_name(mp4file)

			mp4file = os.path.join(mp4dir,video_id+'.mp4')
			transcript_file = os.path.join(transcript_dir,video_id+'.txt')

			os.remove(transcript_file)
			print('Removing {}'.format(transcript_file))

			os.remove(mp4file)
			print('Removing {}'.format(mp4file))
	else:
		print(f'Successfully converted all {numfiles} audio with no errors')

# -------------------------------------Getting IDs----------------------------------------------------- #

def write2file_ids(video_ids, outfile):
    '''
	Write list of video ids to text file

	'''

    with open(outfile, "w", encoding="utf-8") as id_file:
        for video_id in video_ids:
            id_file.write(video_id + "\n")


def get_video_ids(youtube_links, language=['id'], verbose=False, use_manual=True):
    '''
	This function will attempt to fetch the video ids

	'''

    langs = ' '.join(language)
    num_links = len(youtube_links)
    if use_manual:
        t_type = 'manual'
    else:
        t_type = 'auto'

    print('Attempting to fetch {} video ids for {} links'.format(t_type, num_links))

    video_ids = []
    for i, (duration, link) in enumerate(youtube_links):
        if verbose:
            print('Fetching {} out of {} {} videos'.format(
            	i, num_links, langs), end='\r')

	# Get video id from link
        video_id = link.rsplit('=')[-1]

	# NOTE: from above, this part "fixes" the time boundaries of transcription
        video_ids.append(video_id)
        if verbose:
            print('Successfully fetched videos id for '.format(link), end='\r')

    return video_ids


def find_filter_fetch_ids(search_str, outdir,
                          language=['id'],
                          num_pages=100,
                          min_duration=100,
                          channel_only=False,
                          verbose=False,
                          use_manual=False):
    '''
	Main function to find/filter/fetch video ids

	The video ids will be saved to outdir as <channel_name>.txt
	In the format: <video_id> PER LINE

	'''

    long_links = search_links(
    	search_str, num_pages, min_duration, verbose, channel_only)
    video_ids = get_video_ids(long_links, language, verbose, use_manual)

    outfile = os.path.join(outdir, search_str+'.txt')

    #write to a txt file
    write2file_ids(video_ids, outfile)


# ------------------------------------------------------------------------------------------ #
# Search settings
parser = argparse.ArgumentParser(description='Find, filter, fetch transcripts and download audio from youtube')

parser.add_argument("--search-terms", nargs = "+", 
			default = ['tribunnews','metrotvnews','KOMPASTV','detikcom'],
			metavar = 'List of strings',
			help = 'Search terms for youtube videos')


parser.add_argument("--language", nargs = "+", 
			default = ['id'],
			metavar = 'List of strings',
			help = 'Language id of transcription to be downloaded')


parser.add_argument('--num-pages', type = int, 
			default = 100,
			metavar = 'Integer',
			help = 'Number of search result pages to crawl from (default: 100)')

parser.add_argument('--min-duration', type = int, 
			default = 1200,
			metavar = 'Integer',
			help = 'Minimum duration of video, in seconds (default: 1200, i.e. 20mins)')

parser.add_argument('--sample-rate', type = int, 
			default = 16000,
			metavar = 'Integer',
			help = 'Sampling rate of output wav (default: 16kHz)')

parser.add_argument('--wav-dir', type = str,
			default = 'wav',
			help='Directory for wav files (Default: wav/)')


parser.add_argument('--mp4-dir', type = str,
			default = 'mp4',
			help='Directory for mp4 files (Default: mp4/)')


parser.add_argument('--transcripts-dir', type = str,
			default = 'transcripts',
			help='directory for transcription files (default: transcripts/)')

parser.add_argument('--verbose', action = 'store_true',
			help = 'Set verbosity level (Default: False)')

parser.add_argument('--to-wav', action = 'store_true',
			help = 'Convert downloaded mp4 audio to wav (Default: False)')


parser.add_argument('--as-video', action = 'store_true',
			help = 'Download video instead of audio (Default: False)')

parser.add_argument('--channel-only', action = 'store_true',
			help = 'Search by channel name only (Default: False)')

parser.add_argument('--audio-only', action = 'store_true',
			help = 'Search by channel name only (Default: False)')

parser.add_argument('--use-manual', action = 'store_true',
			help = 'Fetch manual transcription only (Default: False)')

parser.add_argument('--id-only', action='store_true',
                    help='Fetch video ids only (Default: False)')

parser.add_argument('--ids-dir', type=str,
                    default='videos_ids/',
                    help='directory for transcription files (default: videos_ids/)')




if __name__ == '__main__':
	# Specify inputs
	args = parser.parse_args()
	search_strs = parse_search_terms(args.search_terms)
	transcript_dir = args.transcripts_dir
	mp4_dir = args.mp4_dir
	wav_dir = args.wav_dir
	is_ids = args.id_only

	# Optional inputs
	language_ids = args.language		# 'id' for indonesian, 'en' for english etc
	num_pages = args.num_pages		# Number of pages in search results to look for
	min_duration = args.min_duration	# Minimum duration of video
	verbose = args.verbose			# Verbosity level
	as_video = args.as_video		# Download video instead of audio only
	channel_only = args.channel_only	# Return search results from channel only
	sample_rate = args.sample_rate		# Sampling rate of output wav files
	audio_only = args.audio_only		# Get audio regardless of transcript availability
	use_manual = args.use_manual		# Fetch manual transcription only

	print(args)

	# Save as audio or video
	if as_video:
		to_wav = False
	else:
		to_wav = args.to_wav


	if(not is_ids):
		if not audio_only:
			# If need to transcription and audio
			check_dir(transcript_dir)
			check_dir(mp4_dir)

			for search_str in search_strs:
				find_filter_fetch_transcripts(search_str, transcript_dir,
								language = language_ids,
								num_pages = num_pages,
								min_duration = min_duration,
								channel_only = channel_only,
								verbose = verbose,
								use_manual= use_manual)

			# only download audio whenever transcript is available
			download_audio_fetched(transcript_dir, mp4_dir, as_video)

			if to_wav:
				# Convert to wav if needed
				check_dir(wav_dir)

				convert2wav(mp4_dir, wav_dir, transcript_dir, sample_rate)
				folders_check(transcript_dir, wav_dir)
			else:
				folders_check(transcript_dir, mp4_dir)

			numfiles = len(os.listdir(transcript_dir))
			print(f'Completed crawling, downloaded {numfiles} files')

		else:
			# If just audio-only, no need to fetch transcriptions
			check_dir(mp4_dir)

			long_links = []
			for search_str in search_strs:
				long_links += search_links(search_str, num_pages, min_duration,
								verbose, channel_only)

			# Get the video links based on the same criterion
			video_ids = [link.split('=')[-1] for _, link in long_links]
			download_video_ids(video_ids, mp4_dir, as_video)

			if to_wav:
				# Convert to wav if needed
				check_dir(wav_dir)

				mp4files = [os.path.join(mp4_dir,f) for f in os.listdir(mp4_dir)]
				convertmp4(mp4files, wav_dir, sample_rate)
				numfiles = len(os.listdir(wav_dir))
			else:
				numfiles = len(os.listdir(mp4_dir))

			print(f'Completed crawling, downloaded {numfiles} files')
			clean_up()

	else:
		ids_dir = args.ids_dir

		# If need channel dir
		check_dir(ids_dir)

		for search_str in search_strs:
			find_filter_fetch_ids(search_str, ids_dir,
							language=language_ids,
							num_pages=num_pages,
							min_duration=min_duration,
							channel_only=channel_only,
							verbose=verbose)

		numfiles = len(os.listdir(ids_dir))
		print(f'Completed crawling, downloaded {numfiles} files')