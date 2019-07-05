import sys
import time
import csv as csv_lib
import datetime
import tweepy
import simplejson as json

import message_recognizers
import utils
from load_tweets import save_tweets

MISSING_FIELD_VALUE = ''


def dump_with_timestamp(text, category="Unknown"):
    print("(%s)--%s--%s" % (category, datetime.datetime.now(), text))


def dump_stream_data(stream_data):
    dump_with_timestamp(stream_data)


class StreamListener(tweepy.StreamListener):
    """
    Tweepy StreamListener that dumps tweets to stdout.
    """

    def __init__(self, opts, logger, api=None):
        super(StreamListener, self).__init__(api=api)
        self.opts = opts
        self.csv_writer = csv_lib.writer(sys.stdout)
        self.running = True
        self.first_message_received = None
        self.status_count = 0
        self.logger = logger

        # Create a list of recognizer instances, in decreasing priority order.
        self.recognizers = (
            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_status_and_dispatch,
                match_string='"in_reply_to_user_id_str":'),

            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_limit_and_dispatch,
                match_string='"limit":{'),

            message_recognizers.DataContainsRecognizer(
                handler_method=self.parse_warning_and_dispatch,
                match_string='"warning":'),

            message_recognizers.DataContainsRecognizer(
                handler_method=self.on_disconnect,
                match_string='"disconnect":'),

            # Everything else is sent to logger
            message_recognizers.MatchAnyRecognizer(
                handler_method=self.on_unrecognized),
        )

    def on_unrecognized(self, stream_data):
        self.logger.warn("Unrecognized: %s", stream_data.strip())

    def on_disconnect(self, stream_data):
        msg = json.loads(stream_data)
        self.logger.warn("Disconnect: code: %d stream_name: %s reason: %s",
                         utils.resolve_with_default(msg, 'disconnect.code', 0),
                         utils.resolve_with_default(msg, 'disconnect.stream_name', 'n/a'),
                         utils.resolve_with_default(msg, 'disconnect.reason', 'n/a'))

    def parse_warning_and_dispatch(self, stream_data):
        try:
            warning = json.loads(stream_data).get('warning')
            return self.on_warning(warning)
        except json.JSONDecodeError:
            self.logger.exception("Exception parsing: %s" % stream_data)
            return False

    def parse_status_and_dispatch(self, stream_data):
        """
        Process an incoming status message.
        """
        status = tweepy.models.Status.parse(self.api, json.loads(stream_data))
        if self.tweet_matchp(status):
            self.status_count += 1
            if self.should_stop():
                self.running = False
                return False

        save_tweets([stream_data.strip()])
        print(stream_data.strip())

    def parse_limit_and_dispatch(self, stream_data):
        return self.on_limit(json.loads(stream_data)['limit']['track'])

    def is_retweet(self, tweet):
        return hasattr(tweet, 'retweeted_status') \
               or tweet.text.startswith('RT ') \
               or ' RT ' in tweet.text

    def tweet_matchp(self, tweet):
        """Return True if tweet matches selection criteria...
        Currently this filters on self.opts.lang if it is not nothing...
        """
        if self.opts.no_retweets and self.is_retweet(tweet):
            return False

        else:
            return True

    def on_warning(self, warning):
        self.logger.warn("Warning: code=%s message=%s" % (warning['code'], warning['message']))
        # If code='FALLING_BEHIND' buffer state is in warning['percent_full']

    def on_error(self, status_code):
        self.logger.error("StreamListener.on_error: %r" % status_code)
        if status_code != 401:
            self.logger.error(" -- stopping.")
            # Stop on anything other than a 401 error (Unauthorized)
            # Stop main loop.
            self.running = False
            return False

    def on_timeout(self):
        """Called when there's a timeout in communications.
        Return False to stop processing.
        """
        self.logger.warn('on_timeout')
        return  ## Continue streaming.

    def on_data(self, data):
        if not self.first_message_received:
            self.first_message_received = int(time.time())

        if self.should_stop():
            self.running = False
            return False  # Exit main loop.

        for r in self.recognizers:
            if r.match(data):
                if r.handle_message(data) is False:
                    # Terminate main loop.
                    self.running = False
                    return False  # Stop streaming
                # Don't execute any other recognizers, and don't call base
                # on_data() because we've already handled the message.
                return
        # Don't execute any of the base class on_data() handlers.
        return

    def should_stop(self):
        """
        Return True if processing should stop.
        """
        if self.opts.duration:
            if self.first_message_received:
                et = int(time.time()) - self.first_message_received
                flag = et >= self.opts.duration
                if flag:
                    self.logger.debug("Stop requested due to duration limits (et=%d, target=%d seconds).",
                                      et,
                                      self.opts.duration)
                return flag
        if self.opts.max_tweets and self.status_count > self.opts.max_tweets:
            self.logger.debug("Stop requested due to count limits (%d)." % self.opts.max_tweets)
            return True
        return False
