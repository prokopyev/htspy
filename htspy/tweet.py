class Tweet:
    def __init__(self, tweet):
        self.__tweet = tweet
        self.__value = self.parse_tweet()

    @property
    def value(self):
        return self.__value

    @property
    def id(self):
        return self.value['_id']
        
    def parse_tweet(self):
        d = {
            "_id": self.__tweet.id,
            "text": self.__tweet.text,
            "coordinates": self.__tweet.coordinates,
            "created_at": self.__tweet.created_at,
            "entities": self.__parse_entities(self.__tweet.entities),
            "favorite_count": self.__tweet.favorite_count,
            "retweet_count": self.__tweet.retweet_count,
            "is_retweet": self.__parse_is_retweet(self.__tweet),
            "user": {
                "screen_name": self.__tweet.user.screen_name,
                "name": self.__tweet.user.name,
                "id_str": self.__tweet.user.id_str
            }
        }

        if not d['coordinates']:
            d.pop('coordinates')
    
        return d

    @staticmethod
    def __parse_entities(entities):
        urls = []
        mentions = []
        hashtags = []

        for i in range(len(entities['urls'])):
            urls.append(entities['urls'][i]['expanded_url'])

        for i in range(len(entities['user_mentions'])):
            mentions.append({
                "screen_name": entities['user_mentions'][i]['screen_name'],
                "name": entities['user_mentions'][i]['name']
            })

        for i in range(len(entities['hashtags'])):
            hashtags.append(entities['hashtags'][i]['text'])

        d = {
            'urls': urls,
            'user_mentions': mentions,
            'hashtags': hashtags
        }
        # Remove any keys that have an empty array value
        return dict((k, v) for k, v in d.items() if v)

    @staticmethod
    def __parse_is_retweet(tweet):
        return hasattr(tweet, 'retweeted_status')