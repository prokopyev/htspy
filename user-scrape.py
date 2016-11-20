from htspy.scrape import scrape_user
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Begin a scrape of the Twitter search feed for all tweets matching any of the '
                    'search terms specified in the terms argument. Sweeps backwards from the '
                    'most recent date to the latest date.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    ag = parser.add_argument
    ag('--api-key', type=str, default=None,
       help='Twitter [API_KEY] value to use for the data pull.')

    ag('--api-secret', type=str, default=None,
       help='Twitter [API_SECRET] value to use for the data pull.')

    ag('--handle', type=str, default=None,
       help='A user Twitter handle to scrape tweets for.')

    ag('--collection', type=str, default=None,
       help='The name of the MongoDB collection which results should be saved to.')

    ag('--resume-id', type=int, default=0,
       help='An integer representing the Tweet Id where the scrape should begin from. A default value of 0 means the '
            'scrape will begin at the end-date value or earliest available Tweet Id in the database. '
            'Providing a value will begin the scrape at (ID-1).')

    ag('--user', type=str, default=None,
       help='The MongoDB user name for authentication.')

    ag('--password', type=str, default=None,
       help='The MongoDB password for authentication.')

    ag('--authDatabase', type=str, default=None,
       help='The MongoDB authentication database.')

    args = parser.parse_args()

    scrape_user(handle=args.handle,
                api_key=args.api_key,
                api_secret=args.api_secret,
                collection=args.collection,
                resume_id=args.resume_id,
                mongo_user=args.user,
                mongo_pw=args.password,
                mongo_auth=args.authDatabase
                )
