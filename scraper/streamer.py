import sys
import time

import logging
import tweepy

import args
import utils
from listener import StreamListener
from settings import ACCESS_KEY, ACCESS_SECRET, CONSUMER_KEY, CONSUMER_SECRET

logger = logging.getLogger(__name__)

"""
    List of named location query (--location-query) names and their
    associated bounding boxes (longitude, latitude) (what is the name of that standard?  geoJSON?)
    Recursive lookups:
    If a value is string, it's a reference to a named entry in the table.  Use the remainder of the
    value string as the new lookup key.
"""


def make_filter_args(opts):
    kwargs = {}
    if opts.track:
        kwargs['track'] = opts.track
    if opts.stall_warnings:
        kwargs['stall_warnings'] = True
    if opts.follow:
        kwargs['follow'] = opts.follow
    return kwargs


def process_tweets(opts):
    """Set up and process incoming streams."""
    try:
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    except KeyError as e:
        logger.error('You must set the %s API key environment variable.', e)
        return

    logger.debug('Init tweepy.Stream()')
    logger.debug(opts)
    listener = StreamListener(opts=opts, logger=logger)
    streamer = tweepy.Stream(auth=auth, listener=listener, retry_count=9999,
                             retry_time=1, buffer_size=16000)

    try:
        kwargs = make_filter_args(opts)
    except ValueError as e:
        listener.running = False
        sys.stderr.write("%s: error: %s\n" % (__file__, e.message))
        return

    while listener.running:
        try:
            try:
                logger.debug('streamer.filter(%s)' % kwargs)
                streamer.filter(**kwargs)
            except TypeError as e:
                if 'stall_warnings' in e.message:
                    logger.warn(
                        "Installed Tweepy version doesn't support stall_warnings parameter.  Restarting without "
                        "stall_warnings parameter.")
                    del kwargs['stall_warnings']
                    streamer.filter(**kwargs)
                else:
                    raise

            logger.debug('Returned from streaming...')
        except IOError:
            if opts.terminate_on_error:
                listener.running = False
            logger.exception('Caught IOError')
        except KeyboardInterrupt:
            # Stop the listener loop.
            listener.running = False
        except Exception:
            listener.running = False
            logger.exception("Unexpected exception.")

        if listener.running:
            logger.debug('Sleeping...')
            time.sleep(5)


def initiate_stream(opts):
    utils.init_logger(logger, opts.log_level)
    process_tweets(opts)


if __name__ == "__main__":
    opts = args.parse_command_line()

    if not opts.track:
        sys.stderr.write(
            '%s: error: Must provide list of track keywords.\n' % __file__)
        sys.exit()
    initiate_stream(opts)
