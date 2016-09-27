# htspy - Hashtag Twitter Scrape Py
Captures tweets matching a group of hashtags for a specified date range into a local MongoDB instance. Tweets are captured in reverse chronological order. Start & end date are based on UTC time. Presently a small script for myself. Functioning work in progress.

## Instructions
1. Create a local MongoDB instance and update constants.py with the appropiate DB & collection names
2. Install pymongo and tweepy using PIP
3. Create a Query object with start_date, end_date, and hashtag variables. Date format is YYYY-MM-DD. Do not use '#' symbol hashtags, they are automatically added
4. Call scrape(query, consumer_key, consumer_secret, resume_last). The final argument specifies whether tweets should restart from the last available one using the smallest tweet_id in MongoDB. Use False for a new scrape.

Example code

```python
from lib.scrape import Query, scrape

hashtags = [
    'tag1',
    'tag2',
    'tag3',
    'tag4'
]

q = Query('2016-09-21', '2016-09-27', hashtags)
scrape(q, apikey, apisecret, False)
```
