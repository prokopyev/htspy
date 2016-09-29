from htspy.scrape import scrape, Query
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

    ag('--start-date', type=str, default=None,
       help='Starting date (earliest date) as YYYY-MM-DD for the search window. '
            'Scrape will stop at 00:00:00 on this date as tweets are grabbed in reverse chronological order.')

    ag('--end-date', type=str, default=None,
       help='Ending date (latest date) as YYYY-MM-DD for the search window. '
            'Scrape will start at 23:59:59 as 1 second prior to this date as tweets are grabbed in reverse '
            'chronological order.')

    ag('--terms', type=str, default=None,
       help='A comma separated string array containing one or more terms or hashtags which the query should search for. '
            'Each term is joined using an OR statement resulting in tweets matching any of the defined terms.')

    ag('--resume-id', type=int, default=0,
       help='An integer representing the Tweet Id where the scrape should begin from. A default value of 0 means the '
            'scrape will begin at the end-date value or earliest available Tweet Id in the database. '
            'Providing a value will begin the scrape at (ID-1).')

    args = parser.parse_args()

    terms = str(args.terms).split(',')

    qry = Query(start_date=args.start_date,
                end_date=args.end_date,
                terms=terms)

    scrape(query=qry,
           api_key=args.api_key,
           api_secret=args.api_secret,
           resume_id=args.resume_id
           )