# htspy - Helpful Twitter Scraper for Python
Wrapper for tweepy which makes it easier to capture all tweets matching a group of hashtags or terms for a specified date range into a local MongoDB instance. Only a date range and search terms are required. The remainder of the save and iteration logic is handled by the wrapper.

## Instructions
1. Create a local MongoDB instance and update constants.py with the appropriate DB & collection names
2. Install pymongo and tweepy using PIP
3. Run tweets-scrape with the required arguments

Example code

```
tweets-scrape.py 
--api-key yourkey
--api-secret yoursecret
--start-date 2016-09-26 
--end-date 2016-09-28 
--terms food,burgers,#bbq
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
1. The optional --restart-id argument allows for manually specifying where the scrape should restart from. This is used to override the default logic where the restart-id is presumed to be the earliest/smalled tweet_id value in the database.
2. It is presently best to keep a fixed end-date value as tweets are returned in reverse chronological order by the API. Otherwise you will have to manually identify the "gap" by setting --restart-id to restart from the correct location.
3. Favorite & retweet counts are as of the time of the scrape. Thus even the same past tweet could have different counts if it accumulated new favorites or retweets since the previous scrape.
