import pymongo
import json
import datetime

class MongoDB:
    def __init__(self, db, collection, user=None, pw=None, auth=None):
        self.__db = db
        self.__collection = collection
        self.__user=user,
        self.__pw=pw,
        self.__auth=auth

    def __mongo_collection(self):
        client = pymongo.MongoClient(self.__get_uri('localhost',self.__user, self.__pw, self.__auth))
        db = client.get_database(self.__db)
        return db.get_collection(self.__collection)

    @staticmethod
    def __get_max_tweet(tweets):
        v = -1
        for t in tweets:
            if t['_id'] > v:
                v = t['_id']

        return v


    @staticmethod
    def __get_uri(host, user=None, pw=None, auth_db=None):
        if not (user and pw and auth_db):
            s = 'mongodb://{HOST}:27017'.format(
                HOST=host
            )
        else:
            s = 'mongodb://{USER}:{PASS}@{HOST}:27017/{DB}'.format(
                HOST=host,
                USER=user,
                PASS=pw,
                DB=auth_db
            )
        return s


    def mongo_save(self, tweets):
        if len(tweets) == 0:
            raise ValueError('No tweets available to save')

        try:
            self.__mongo_collection().insert_many(tweets)
            print('Saved {X} tweets to MongoDB at {TIME}'.format(
                X=len(tweets),
                TIME=datetime.datetime.now().isoformat()
            ))
        except pymongo.errors.BulkWriteError as e:
            # Fall back to importing one at a time until failure
            i = 0
            try:
                print('Bulk insert failed, falling back to single insert mode...')
                for tweet in tweets:
                    self.__mongo_collection().insert(tweet)
                    i += 1
                    print('Single insert record: {I}'.format(I=i))
            except pymongo.errors.BulkWriteError as e:
                raise ImportError('Failed to write batch to MongoDB. Check for duplication. Failed at: {ID}'.format(
                    ID=tweets[i]['_id']
                ))


    def mongo_to_json(self, path):
        tweets = self.mongo_get_tweets()

        with open(path, 'w') as outfile:
            for tweet in tweets:
                tweet['created_at'] = tweet['created_at'].isoformat()
                tweet['screen_name'] = tweet['user']['screen_name']
                tweet['user_name'] = tweet['user']['name']
                tweet.pop('user')
                outfile.write(json.dumps(tweet) +'\n')


    def mongo_get_tweets(self):
        collection = self.__mongo_collection()

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


    def mongo_get_oldest(self):
        # Tweets are returned in reverse order so by querying for the oldest record we know where to pick up
        # if we need to restart the capture.
        collection = self.__mongo_collection()

        obj = collection.find({}, {'_id': 1}).sort('_id', pymongo.ASCENDING).limit(1)
        if obj.count() == 0:
            return False
        else:
            return obj[0]['_id']