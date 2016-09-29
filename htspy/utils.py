import pymongo
import json
import datetime
from htspy.constants import *


def __mongo_collection():
    client = pymongo.MongoClient()
    db = client.get_database(MONGO_DB)
    return db.get_collection(MONGO_COLLECTION)


def __get_max_tweet(tweets):
    v = -1
    for t in tweets:
        if t['_id'] > v:
            v = t['_id']

    return v


def mongo_save(tweets):
    if len(tweets) == 0:
        raise ValueError('No tweets available to save')

    try:
        __mongo_collection().insert_many(tweets)
        print('Saved {X} tweets to MongoDB at {TIME}'.format(
            X=len(tweets),
            TIME=datetime.datetime.now().isoformat()
        ))
    except pymongo.errors.BulkWriteError as e:
        raise ImportError('Failed to write batch to MongoDB. Check for duplication. Max Tweet Id in batch: {ID}'.format(
            ID=__get_max_tweet(tweets)
        ))


def mongo_to_json(path):
    tweets = mongo_get_tweets()

    with open(path, 'w') as outfile:
        for tweet in tweets:
            tweet['created_at'] = tweet['created_at'].isoformat()
            tweet['screen_name'] = tweet['user']['screen_name']
            tweet['user_name'] = tweet['user']['name']
            tweet.pop('user')
            outfile.write(json.dumps(tweet) +'\n')


def mongo_get_tweets():
    collection = __mongo_collection()

    tweets = collection.find({}, {
        '_id': 0,
        'tweet_id': 1,
        'created_at': 1,
        'user.screen_name': 1,
        'user.name': 1,
        'retweet_count': 1,
        'favorite_count': 1,
        'is_retweet': 1,
        'text': 1
    })
    return tweets


def mongo_get_oldest():
    # Tweets are returned in reverse order so by querying for the oldest record we know where to pick up
    # if we need to restart the capture.
    collection = __mongo_collection()

    obj = collection.find({}, {'_id': 1}).sort('_id', pymongo.ASCENDING).limit(1)
    if obj.count() == 0:
        return False
    else:
        return obj[0]['_id']