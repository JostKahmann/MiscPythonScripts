from youtube_transcript_api import YouTubeTranscriptApi as ytapi

import shlex


def print_help():
    print("""Usage:

    help                                            prints this message
    lang <language>                                 sets the language to retrieve the transcript for (default en)
    print <video-id> [start=0] [end=∞]              prints the transcript of the video to console from start to end
    save <video-id> <to-path> [start=0] [end=∞]     saves the transcript of the video to the given path
                                                        start/end may be in seconds or [hh:]mm:ss
    thumb <video-id>                                print links to thumbnail (best, high, medium and low quality)
    
    exit                                            exit the application
    """)


def as_timestamp(timestamp):
    """
    Transforms a number of seconds to a readable timestamp
    :param timestamp: number of seconds
    :return: timestamp as string
    """
    seconds = timestamp % 60
    minutes = timestamp // 60 % 60
    hours = timestamp // 3600
    if hours > 0:
        return f"{hours}:{minutes:02}:{seconds:02}"
    return f"{minutes}:{seconds:02}"


def parse_timestamp(timestamp):
    """
    Transforms the timestamp to a float equal to the number of seconds represented by the timestamp
    :param timestamp: format may be seconds or [hh:][m]m:[s]s
                      note that any number of seconds, minutes or hours will be parsed
                      so 0:120:9999 can be a valid albeit nonsensical input (=> 17199.0)
    :return: timestamp as float
    """
    if str(timestamp).find(':') == -1:
        return float(timestamp)
    splits = reversed(timestamp.split(':'))
    time = 0.0
    mul = 1
    for split in splits:
        time += float(split) * mul
        mul *= 60
    return time


def fetch_transcript(lang, video_id, start_str, end_str):
    """
    Fetches a transcript from the YouTube API
    :param lang: language of the transcript
    :param video_id: video id (youtube.com/watch?v=<video_id>)
    :param start_str: timestamp the result should start at
    :param end_str: timestamp the result should end at
    :return: transcript as string
    """
    try:
        transcript = ytapi.get_transcript(video_id, languages=[lang])
    except Exception as e:
        print(e.args[0])
        return ""

    start = parse_timestamp(start_str)
    end = parse_timestamp(end_str)
    content = []
    for entry in transcript:
        text = entry['text']
        time = float(entry['start'])
        # duration = entry ['duration']
        if float(start) <= time <= float(end):
            content.append(f"[{as_timestamp(int(time))}]: {text}")
    return "\n".join(s for s in content)


def print_transcript(lang, video_id, start='0', end='inf'):
    """
    Prints a transcript to the console
    :param lang: language of the transcript
    :param video_id: video id (youtube.com/watch?v=<video_id>)
    :param start: timestamp the result should start at
    :param end: timestamp the result should end at
    :return: void
    """
    print(fetch_transcript(lang, video_id, start, end))


def save_transcript(lang, video_id, path, start='0', end='inf'):
    """
    Saves a transcript to a file
    :param lang: language of the transcript
    :param video_id: video id (youtube.com/watch?v=<video_id>)
    :param path: path to save to (relative or absolute)
    :param start: timestamp the result should start at
    :param end: timestamp the result should end at
    :return: void
    """
    content = fetch_transcript(lang, video_id, start, end)
    if not content.strip():
        print("\n\nDid not write file since no content was returned")
        return
    with open(path, 'w') as file:
        file.write(content)


def input_loop():
    lang = 'en'
    while True:
        user_input = input('> ').strip()
        if user_input in ['exit', 'q', 'esc']:
            return
        if user_input in ['help', '?']:
            print_help()
            continue
        argv = shlex.split(user_input)
        if argv[0] == 'print':
            print_transcript(lang, *argv[1:])
        elif argv[0] == 'save':
            save_transcript(lang, *argv[1:])
        elif argv[0] == 'lang':
            lang = argv[1]
        elif argv[0] == 'thumb':
            for q in ['maxres', 'hq', 'mq', 'sd']:
                print(f"https://img.youtube.com/vi/{argv[1]}/{q}default.jpg")
        else:
            print(f"Unknown command \"{argv[0]}\", type \"help\" for help")


print('Youtube Transcript Downloader\nType "help" for help')
input_loop()
