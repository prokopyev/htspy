from htspy.scrape import scrape_network
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Gets the specified MongoDB collection of tweets and creates a unique list of user handles '
                    'sorted by descending order of max(tweet_id). A total of N tweets are returned for '
                    'the top M users. If a restart handle is passed, then the scrape will begin from that id onward.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ag = parser.add_argument
    ag('--api-key', type=str, default=None,
       help='Twitter [API_KEY] value to use for the data pull.')

    ag('--api-secret', type=str, default=None,
       help='Twitter [API_SECRET] value to use for the data pull.')

    ag('--src-collection', type=str, default=None,
       help='The name of the MongoDB collection which contains the handles to scrape.')

    ag('--dst-collection', type=str, default=None,
       help='The name of the MongoDB collection which results should be saved to.')

    ag('--restart-handle', type=str, default=None,
       help='In case of failure, the Twitter handle at which the process should start from')

    ag('--max-tweets', type=int, default=None,
       help='Maximum number of tweets per handle to retrieve')

    ag('--max-handles', type=int, default=0,
       help='Maximum number of handles to retrieve')

    ag('--user', type=str, default=None,
       help='The MongoDB user name for authentication.')

    ag('--password', type=str, default=None,
       help='The MongoDB password for authentication.')

    ag('--authDatabase', type=str, default=None,
       help='The MongoDB authentication database.')

    args = parser.parse_args()

    scrape_network(
                api_key=args.api_key,
                api_secret=args.api_secret,
                mongo_user=args.user,
                mongo_pw=args.password,
                mongo_auth=args.authDatabase,
                src_collection=args.src_collection,
                dst_collection=args.dst_collection,
                restart_handle=args.restart_handle,
                user_max_tweets=args.max_tweets,
                max_handles=args.max_handles
                )
