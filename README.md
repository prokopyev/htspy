# htspy
Captures tweets matching a group of hashtags for a specified date range into a local MongoDB instance. Tweets are captured in reverse chronological order. Start & end date are based on UTC time.

## Instructions
1. Create a MongoDB project and update constants.py with the appropiate DB & collection names
2. Create a Query object with start_date, end_date, and hashtag variables
3. Call scrape(query, consumer_key, consumer_secret, resume_last). The final argument specifies whether tweets should restart from the last available one in MongoDB. Use False for a new scrape

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
