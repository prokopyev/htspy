import tweepy
import datetime
from time import sleep
from htspy.constants import *
from htspy.tweet import Tweet
import htspy.utils as utils


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
            return '%20OR%20' + term
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


def __twitter_get_api(api_key, api_secret):
    auth = tweepy.AppAuthHandler(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return api

def __twitter_get_page(query, api, collection, resume_id=0):
    page_len = 1
    while page_len > 0:
        if resume_id > 0:
            page = api.search(q=query.value, locale="en", lang="en", count=TWEET_PER_CALL, result_type='recent',
                              max_id=resume_id)
        else:
            page = api.search(q=query.value, locale="en", lang="en", count=TWEET_PER_CALL, result_type='recent')
            resume_id=0

        batch_tweets = []
        page_len = len(page)

        if page_len > 0:
            for tweet in page:
                if tweet.id != resume_id:
                    batch_tweets.append(Tweet(tweet).value)

            db = utils.MongoDB('twitter', collection)
            db.mongo_save(batch_tweets)
            resume_id = page[-1].id
            sleep(TWEET_REST_TIME)
        else:
            return False


def __twitter_get_user(handle, api, collection, resume_id=0):

    if resume_id>0:
        user_tweets = api.user_timeline(screen_name=handle, count=200, max_id=resume_id-1)
    else:
        user_tweets = api.user_timeline(screen_name=handle, count=200)

    while len(user_tweets)>0:
        batch_tweets = []

        for tweet in user_tweets:
            batch_tweets.append(Tweet(tweet).value)

        db = utils.MongoDB('twitter', collection)
        db.mongo_save(batch_tweets)
        resume_id = user_tweets[-1].id - 1
        sleep(TWEET_REST_TIME)

        user_tweets = api.user_timeline(screen_name=handle, count=200, max_id=resume_id)

    return False



def scrape(query, api_key, api_secret, collection, resume_id=0, mongo_user=None, mongo_pw=None, mongo_auth=None):
    api = __twitter_get_api(api_key, api_secret)
    error_count = 0
    continue_loop = True

    while error_count < TWEET_MAX_RESTARTS and continue_loop:
        if resume_id > 0:
            print("Scrape: Resume from Tweet ({ID})".format(ID=resume_id))
        else:
            db = utils.MongoDB('twitter', collection, user=mongo_user, pw=mongo_pw, auth=mongo_auth)
            resume_id = db.mongo_get_oldest()
            if not resume_id:
                print("Scrape: Start from {DATE}".format(
                    DATE=query.end_date
                ))
            else:
                print("Scrape: Resume from Tweet ({ID})".format(ID=resume_id))


        try:
            continue_loop = __twitter_get_page(query, api, collection, resume_id)
        except ImportError as e:
            print("MongoDB Error: ({E})".format(E=e))
            continue_loop = False
            error_count = TWEET_MAX_RESTARTS
        except Exception as e:
            error_count += 1
            print("Other Error: Probably connection related. Retrying in 180s. ({E})".format(E=e))
            sleep(180)

    if error_count >= TWEET_MAX_RESTARTS:
        print("Scrape: Finished with errors @ {DATE}".format(
            DATE=datetime.datetime.now().isoformat()
        ))
    elif not continue_loop:
        print("Scrape: Finished without errors @ {DATE}".format(
            DATE=datetime.datetime.now().isoformat()
        ))


def scrape_user(handle, api_key, api_secret, collection, resume_id=None, mongo_user=None, mongo_pw=None,
                mongo_auth=None):
    api = __twitter_get_api(api_key, api_secret)
    error_count = 0
    continue_loop = True

    while error_count < TWEET_MAX_RESTARTS and continue_loop:
        print("Scrape: Resume from Tweet ({ID})".format(ID=resume_id))

        try:
            continue_loop = __twitter_get_user(handle, api, collection)
        except ImportError as e:
            print("MongoDB Error: ({E})".format(E=e))
            continue_loop = False
            error_count = TWEET_MAX_RESTARTS
        except Exception as e:
            error_count += 1
            print("Other Error: Probably connection related. Retrying in 180s. ({E})".format(E=e))
            sleep(180)

    if error_count >= TWEET_MAX_RESTARTS:
        print("Scrape: Finished with errors @ {DATE}".format(
            DATE=datetime.datetime.now().isoformat()
        ))
    elif not continue_loop:
        print("Scrape: Finished without errors @ {DATE}".format(
            DATE=datetime.datetime.now().isoformat()
        ))