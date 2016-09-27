import tweepy
from time import sleep
from lib.constants import *
from lib.tweet import Tweet
import lib.utils as utils


class Query:
    def __init__(self, start_date, end_date, hashtags):
        self.start_date = start_date
        self.end_date = end_date
        self.hashtags = hashtags
        self.__value = self.__build_query()

    @property
    def value(self):
        return self.__value

    @staticmethod
    def __hashtag_parse(hashtag, is_multi):
        if is_multi:
            return ' OR #' + hashtag
        else:
            return '#' + hashtag

    def __hashtag_concat(self):
        s = ''
        for h in range(len(self.hashtags)):
            s += self.__hashtag_parse(self.hashtags[h], h > 0)

        return s

    def __build_query(self):
        s = '{HASHTAGS} since:{SINCE} until:{UNTIL}'.format(
            HASHTAGS=self.__hashtag_concat(),
            SINCE=self.start_date,
            UNTIL=self.end_date
        )
        return s


def scrape_with_page(query, api_key, api_secret, restart_id=False):
    auth = tweepy.AppAuthHandler(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    if restart_id:
        cur = tweepy.Cursor(api.search, q=query.value, locale="en", count=TWEET_PER_CALL, result_type='recent',
                            max_id=restart_id).pages()
    else:
        cur = tweepy.Cursor(api.search, q=query.value, locale="en", count=TWEET_PER_CALL, result_type='recent').pages()

    for page in cur:
        batch_tweets = []
        if len(page) > 0:
            for tweet in page:
                if tweet.id != restart_id:
                    batch_tweets.append(Tweet(tweet).value)

            utils.save_to_mongo(batch_tweets)
            sleep(TWEET_REST_TIME)
        else:
            return False


def scrape(query, api_key, api_secret, resume_last):
    error_count = 0
    continue_loop = True
    restart_id = False

    while error_count < SCRAPE_MAX_RESTARTS and continue_loop:
        if resume_last:
            restart_id = utils.mongo_get_oldest()
            print("Resuming from tweet id: {ID}".format(ID=restart_id))
        else:
            print("Scraping backwards from: {DATE}".format(
                DATE=query.end_date
            ))

        try:
            continue_loop = scrape_with_page(query, api_key, api_secret, restart_id)
        except ImportError as e:
            print("MongoDB write error: ({E})".format(E=e))
            continue_loop = False
        except Exception as e:
            print("General error: Probably connection related. Retrying in 180s. ({E})".format(E=e))
            sleep(180)

    if error_count >= 5:
        print("Reached max errors")
    elif not continue_loop:
        print("End of scrape")
