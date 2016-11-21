# htspy - Helpful Twitter Scraper for Python
Wrapper for tweepy which makes it easier to capture all tweets matching a group of hashtags or terms for a specified date range into a local MongoDB instance. Only a date range and search terms are required. The remainder of the save and iteration logic is handled by the wrapper.

## Capeabilities
1. Scrape the Twitter Search API for specific hashtags or terms
2. Scrape a specific user timeline (new)
3. Get the last N tweets for last M unique users who appear in a MongoDB collection of tweets (new)


## Instructions
1. Create a local MongoDB instance and update constants.py with the appropriate DB & collection names
2. Install pymongo and tweepy using PIP
3. Run tweets-scrape with the required arguments below

Example code

Get all tweets containing specific terms
```
tweets-scrape.py 
--api-key yourkey
--api-secret yoursecret
--start-date 2016-09-26 
--end-date 2016-09-28 
--terms food,burgers,#bbq
--collection foodtweets
```

Get all tweets from a specific user
```
user-scrape.py
--api-key yourkey
--api-secret yoursecret
--handle the_user_handle
--collection the_user_tweets
```

Get 100 tweets from all users within an existing MongoDB tweet collection
```
network-scrape.py
--api-key yourkey
--api-secret yoursecret
--src-collection tweet_collection
--dst-collection user_tweets
--max-tweets 100
```
## Captured Fields
1. tweet_id
2. text
3. coordinates
4. created_at
5. entities (urls, mentions, hashtags)
6. favorite_count
7. retweet_count
8. is_retweet
9. user (id, screen name, real name)

## Notes
1. The optional `--restart-id` argument allows for manually specifying where the scrape should restart from. This is used to override the default logic where the restart-id is presumed to be the earliest/smalled tweet_id value in the database.
2. Tweets are returned in reverse chronological order by the API. Try to scrape from newest to oldest in order to avoid confusion as default restart checks for oldest tweet in db.
3. Favorite & retweet counts are as of the time of the scrape. Thus even the same past tweet could have different counts if it accumulated new favorites or retweets since the previous scrape.
4. MongoDB database is always 'twitter' while the collection name may be changed.