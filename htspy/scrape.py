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


def __scrape_get_resumeid(collection, handle=None, mongo_user=None, mongo_pw=None, mongo_auth=None):
    db = utils.MongoDB('twitter', collection, user=mongo_user, pw=mongo_pw, auth=mongo_auth)
    return db.mongo_get_oldest(handle)


def __twitter_get_api(api_key, api_secret):
    auth = tweepy.AppAuthHandler(api_key, api_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    return api


def __twitter_get_page(query, api, collection, resume_id=0):
    if resume_id > 0:
        search_tweets = api.search(q=query.value, locale="en", lang="en", count=TWEET_PER_CALL, result_type='recent',
                          max_id=resume_id-1)
    else:
        search_tweets = api.search(q=query.value, locale="en", lang="en", count=TWEET_PER_CALL, result_type='recent')

    while len(search_tweets)>0:
        batch_tweets = []

        for tweet in search_tweets:
            batch_tweets.append(Tweet(tweet).value)

        db = utils.MongoDB('twitter', collection)
        db.mongo_save(batch_tweets)
        resume_id = search_tweets[-1].id-1
        sleep(TWEET_REST_TIME)

        search_tweets = api.search(q=query.value, locale="en", lang="en", count=TWEET_PER_CALL, result_type='recent',
                          max_id=resume_id-1)

    return False


def __twitter_get_user(handle, api, collection, resume_id=0, max_tweets=0):
    if resume_id>0:
        user_tweets = api.user_timeline(screen_name=handle, count=200, max_id=resume_id-1)
    else:
        user_tweets = api.user_timeline(screen_name=handle, count=200)

    continue_loop = True
    i=0

    while len(user_tweets)>0 and continue_loop:
        batch_tweets = []

        for tweet in user_tweets:
            if max_tweets>0 and i>=max_tweets:
                continue_loop=False
                break
            batch_tweets.append(Tweet(tweet).value)
            i+=1

        db = utils.MongoDB('twitter', collection)
        db.mongo_save(batch_tweets)
        resume_id = user_tweets[-1].id - 1
        sleep(TWEET_REST_TIME)

        user_tweets = api.user_timeline(screen_name=handle, count=200, max_id=resume_id)

    return False


def scrape_search(query, api_key, api_secret, collection, resume_id=0, mongo_user=None, mongo_pw=None, mongo_auth=None):
    api = __twitter_get_api(api_key, api_secret)
    error_count = 0
    continue_loop = True

    while error_count < TWEET_MAX_RESTARTS and continue_loop:
        if resume_id > 0:
            print("Scrape: Resume from Tweet ({ID})".format(ID=resume_id))
        else:

            resume_id = __scrape_get_resumeid(collection,mongo_user=mongo_user, mongo_pw=mongo_pw,
                                              mongo_auth=mongo_auth)
            if not resume_id:
                print("Scrape: Start from {DATE}".format(DATE=query.end_date))
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


def scrape_user(handle, api_key, api_secret, collection, resume_id=0, mongo_user=None, mongo_pw=None, mongo_auth=None):
    api = __twitter_get_api(api_key, api_secret)
    error_count = 0
    continue_loop = True

    while error_count < TWEET_MAX_RESTARTS and continue_loop:
        if resume_id > 0:
            print("Scrape: Resume from Tweet ({ID})".format(ID=resume_id))
        else:

            resume_id = __scrape_get_resumeid(collection,handle=handle, mongo_user=mongo_user, mongo_pw=mongo_pw,
                                              mongo_auth=mongo_auth)
            if not resume_id:
                print("Scrape: Getting tweets for {HANDLE}".format(HANDLE=handle))
            else:
                print("Scrape: Getting tweets for {HANDLE} from Tweet ({ID})".format(HANDLE=handle, ID=resume_id))

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

def scrape_network(api_key, api_secret, src_collection, dst_collection, user_max_tweets, restart_handle=None,
                   max_handles=0, mongo_user=None, mongo_pw=None, mongo_auth=None):
    # Gets all unique Twitter handles in source collection and iterates through each to collect the last N tweets.
    # Can be restarted from a specific Twitter handle
    api = __twitter_get_api(api_key, api_secret)
    db_src = utils.MongoDB('twitter', src_collection, user=mongo_user, auth=mongo_auth, pw=mongo_pw)

    handles = list(db_src.mongo_get_handles())
    start = 0
    print("Found {COUNT} unique handles in {COLLECTION}.".format(COUNT=len(handles), COLLECTION=src_collection))

    if restart_handle:
        start = [x['_id'] for x in handles].index(restart_handle)

    for h in range(start, len(handles)):
        if max_handles>0 and h-start>=max_handles:
            break
        print("Scrape: Getting {COUNT} tweets for {HANDLE}.".format(COUNT=user_max_tweets,
                                                                    HANDLE=handles[h].get('_id')))

        __twitter_get_user(handles[h].get('_id'), api, dst_collection, max_tweets=user_max_tweets)

    print("Scrape: Finished without errors @ {DATE}".format(
        DATE=datetime.datetime.now().isoformat()
    ))



