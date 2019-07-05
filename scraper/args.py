import argparse


def csv_args(value):
    """Parse a CSV string into a Python list of strings.
    Used in command line parsing."""
    return map(str, value.split(","))


def userids_type(value):
    """ Alias for csv_args.  Parse list of userids into array of strings. """
    return csv_args(value)


def duration_type(value):
    """
    Parse 'duration' type argument.
    Format: {number}{interval-code}
    where: number is an integer
    interval-code: one of ['h', 'm', 's'] (case-insensitive)
    interval-code defaults to 's'
    Returns # of seconds.
    """
    import re
    value = value.strip() + ' '  # pad with space which is synonymous with 'S' (seconds).
    secs = {' ': 1, 's': 1, 'm': 60, 'h': 3600, 'd': 86400}
    match = re.match("^(?P<val>\d+)(?P<code>[\ssmhd]+)", value.lower())
    if match:
        val = int(match.group('val'))
        code = match.group('code')
        if not code:
            # Default is seconds (s)
            code = 's'
        else:
            code = code[0]
        return val * secs[code]
    else:
        raise argparse.ArgumentTypeError('Unexpected duration type "%s".' % value.strip())


def parse_command_line():
    parser = argparse.ArgumentParser(description='Twitter Stream dumper')

    parser.add_argument(
        '-f',
        '--fields',
        type=csv_args,
        metavar='field-list',
        help='list of fields to output as CSV columns.  If not set, raw status text (all fields) as a large JSON structure.')

    parser.add_argument(
        '-F',
        '--follow',
        type=userids_type,
        metavar='follow-userid-list',
        help='comma-separated list of Twitter userids (numbers, not names) to follow.'),

    parser.add_argument(
        '-d',
        '--duration',
        type=duration_type,
        metavar='duration-spec',
        help='capture duration from first message receipt.'
             ' Use 5 or 5s for 5 seconds, 5m for 5 minutes, 5h for 5 hours, or 5d for 5 days.'
    )

    parser.add_argument(
        '-m',
        '--max-tweets',
        metavar='count',
        type=int,
        help='maximum number of statuses to capture.'
    )

    parser.add_argument(
        '-l',
        '--log-level',
        default='WARN',
        metavar='log-level',
        help="set log level to one recognized by core logging module.  Default is WARN."
    )

    parser.add_argument(
        '-n',
        '--no-retweets',
        action='store_true',
        help='don\'t include statuses identified as retweets.'
    )

    parser.add_argument(
        '-t',
        '--terminate-on-error',
        action='store_true',
        help='terminate processing on errors.')

    parser.add_argument(
        '--stall-warnings',
        action='store_true',
        help='request stall warnings from Twitter streaming API if Tweepy supports them.')

    parser.add_argument(
        'track',
        nargs='*',
        help='status keywords to be tracked'
    )

    p = parser.parse_args()

    return p
