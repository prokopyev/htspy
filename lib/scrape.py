import tweepy
from time import sleep
from lib.constants import *
from lib.tweet import Tweet
import lib.utils as utils


class Query:
    def __init__(self, start_date, end_date, terms):
        self.start_date = start_date
        self.end_date = end_date
        self.terms = terms
        self.__value = self.__build_query()

    @property
    def value(self):
        return self.__value

    @staticmethod
    def __term_parse(term, is_multi):
        if is_multi:
            return ' OR ' + term
        else:
            return term

    def __term_concat(self):
        s = ''
        for t in range(len(self.terms)):
            s += self.__term_parse(self.terms[t], t > 0)

        return s

    def __build_query(self):
        s = '{TERMS} since:{SINCE} until:{UNTIL}'.format(
            TERMS=self.__term_concat(),
            SINCE=self.start_date,
            UNTIL=self.end_date
        )
        return s


def scrape_with_page(query, api, restart_id=False):
    page_len = 1
    while page_len > 0:
        if restart_id:
            page = api.search(q=query.value, locale="en", count=TWEET_PER_CALL, result_type='recent',
                                 max_id=restart_id)
        else:
            page = api.search(q=query.value, locale="en", count=TWEET_PER_CALL, result_type='recent')
            restart_id=0

        batch_tweets = []
        page_len = len(page)

        if page_len > 0:
            for tweet in page:
                if tweet.id != restart_id:
                    batch_tweets.append(Tweet(tweet).value)

            utils.save_to_mongo(batch_tweets)
            restart_id = page[-1].id
            sleep(TWEET_REST_TIME)
        else:
            return False


def scrape(query, api_key, api_secret, resume_last):
    auth = tweepy.AppAuthHandler(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    error_count = 0
    continue_loop = True
    restart_id = False

    while error_count < SCRAPE_MAX_RESTARTS and continue_loop:
        if resume_last == -1:
            restart_id = utils.mongo_get_oldest()
            print("Resuming from tweet id: {ID}".format(ID=restart_id))
        elif resume_last > 0:
            restart_id = resume_last
            print("Resuming from tweet id: {ID}".format(ID=restart_id))
        else:
            print("Scraping backwards from: {DATE}".format(
                DATE=query.end_date
            ))

        try:
            continue_loop = scrape_with_page(query, api, restart_id)
        except ImportError as e:
            print("MongoDB write error: ({E})".format(E=e))
            continue_loop = False
        except Exception as e:
            error_count += 1
            print("General error: Probably connection related. Retrying in 180s. ({E})".format(E=e))
            sleep(180)

    if error_count >= 5:
        print("Reached max errors")
    elif not continue_loop:
        print("End of scrape")
