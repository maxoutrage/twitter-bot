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


class TStream(tweepy.StreamListener):
    favourite = 0
    retweet = 0

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
            return

        try:
            if not tweet.favorited:
                tweet.favorite()
                TStream.favourite += 1
                print("=" * 60)
                print(f"FAV={TStream.favourite} RET={TStream.retweet}")
                logger.info(f"FAV: {tweet.user.screen_name} {tweet.user.id}")
                logger.info(f'FAV: {tweet.text}')
        except tweepy.TweepError as error:
            logger.error("FV: error becasue {error.reason}")
        try:
            target = tweet.user.id
            for id in RETWEETS:
                if target == id:
                    TStream.retweet += 1
                    tweet.retweet(tweet.id)
                    logger.info(f"RT: {tweet.user.screen_name} {tweet.text}")
            else:
                logger.info("RT: No match")
        except tweepy.TweepError as error:
            logger.error('RT: error because {error.reason}')


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

    tweets_listener = TStream(api)
    stream = tweepy.Stream(api.auth, tweets_listener)
    while True:
        try:
            stream.filter(follow=LIKES)
        except KeyboardInterrupt:
            sys.exit()


if __name__ == "__main__":
    with open("watch-id.txt") as f:
        LIKES = f.read().splitlines()
        logger.info(f"loaded {len(LIKES)} profiles to fav")

    with open("watch-retweet.txt") as f:
        RETWEETS = f.read().splitlines()
        logger.info(f'loaded {len(RETWEETS)} profile to retweet')
    main(LIKES, RETWEETS)
