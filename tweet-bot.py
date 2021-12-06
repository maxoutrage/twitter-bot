#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tweepy
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import logging
import json
import sys
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

consumer_key = os.environ['consumer_key']
consumer_secret = os.environ['consumer_secret']
access_token = os.environ['access_token']
access_token_secret = os.environ['access_token_secret']


class TweetStreamListener(tweepy.StreamListener):
    def __init__(self, api):
        self.api = api
        self.me = api.me()
        favourite = 0
        retweet = 0

    def on_status(self, tweet):
        # decoded = json.loads(tweet)
        # logger.info(f"Processing tweet id {tweet.id}")
        # logger.info(f" from {tweet.user.id}")
        # logger.info(f" as   {tweet.user.screen_name}")
        # logger.info(f" text {tweet.text}")
        if tweet.in_reply_to_status_id is not None or \
                tweet.user.id == self.me.id:
            # This tweet is a reply or I'm its author so, ignore it
            return
        if tweet.text.startswith('RT'):
            # logger.info("Retweet - ignoring")
            return

        # if tweet.user.id == 1367531:
            # tweet.reply

        try:
            if not tweet.favorited:
                tweet.favorite()
                favourite += 1
                print("=" * 50)
                print(f"FAV={favourite} RET={retweet}")
                logger.info(f"FAV: {tweet.user.screen_name} {tweet.user.id}")
                logger.info(f'FAV: {tweet.text}')
                if tweet.user.id in RETWEETS:
                    logger.info(f"RT: {tweet.user.screen_name} {tweet.text}")
                    tweet.retweet()
                    retweet += 1
        except Exception as e:
            logger.error("Error on fav", exc_info=True)

        # if not tweet.retweeted:
            # Retweet, since we have not retweeted it yet
            # try:
            # return
            # tweet.retweet()
            # except Exception as e:
            # logger.error("Error on fav and retweet", exc_info=True)


def create_api():
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True,
                     wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)

    logger.info("API created")
    return api


def followers(api):
    logger.info("Retrieving followers")
    for follower in tweepy.Cursor(api.followers).items():
        if not follower.following:
            logger.info(f"Following {follower.name}")
            follower.follow()


def main(LIKES, RETWEETS):
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = create_api()

    tweets_listener = TweetStreamListener(api)
    stream = tweepy.Stream(api.auth, tweets_listener)
    while True:
        try:
            stream.filter(follow=LIKES)
        except KeyboardInterrupt:
            sys.exit()

    # try:
        # stream.filter(track=keywords, languages=["en"])
    # except KeyboardInterrupt:
        # sys.exit()


if __name__ == "__main__":
    # search = input("Search for? ")
    logger.info(f"Reading tweet files")
    with open("watch-id.txt") as f:
        LIKES = f.read().splitlines()

    print("Following...")
    for f in LIKES:
        print(f)

    with open("watch-retweet.txt") as f:
        RETWEETS = f.read().splitlines()

    main(LIKES, RETWEETS)
