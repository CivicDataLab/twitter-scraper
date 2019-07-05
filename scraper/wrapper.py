from argparse import Namespace

from streamer import initiate_stream

file_name = "hashtags.txt"

if __name__ == "__main__":
    tag_list = [line.rstrip('\n') for line in open(file_name)]

    args = Namespace(duration=None, fields=None, follow=None, log_level='WARN', max_tweets=None, no_retweets=False,
                     stall_warnings=False, terminate_on_error=False, track=tag_list)

    initiate_stream(args)
