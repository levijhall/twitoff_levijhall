from os import getenv
import tweepy
from .models import DB, User, Tweet
import spacy

# Get our API keys from our .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)


def add_or_update_user(username):
    '''take a username and pull that user's data and tweets from the API
    If this user already exists in our database then we will just check to
    see if there are any new tweets from that user that we don;'t already haave
    and we will add any new tweets to the DB.'''

    try:
        # get the user information from Twitter
        twitter_user = TWITTER.get_user(screen_name=username)

        # check to see if this user is already in the database
        # is there a user with the same ID aldready in the database
        # if we don't already have that user, then we'll create a new one
        db_user = User.query.get(twitter_user.id)
        if db_user is None:
            db_user = User(id=twitter_user.id,
                           username=username,
                           name=twitter_user.name,
                           image_url=twitter_user.profile_image_url)

        # add the user to the database
        # this won't re-add a user if they've already been added
        DB.session.add(db_user)

        # print(dir(twitter_user))

        # get the user's tweets (in a list)
        tweets = twitter_user.timeline(count=200,
                                       exclude_replies=True,
                                       include_rts=False,
                                       tweet_mode='extended',
                                       since_id=db_user.newest_tweet_id)

        # update the newest_tweet_id if there have been new tweets
        # since the last time this user tweeted
        if tweets:
            db_user.newest_tweet_id = tweets[0].id

        # add all of the individual tweets to the database
        for tweet in tweets:
            tweet_vect = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                             text=tweet.full_text[:300],
                             vect=tweet_vect,
                             user_id=db_user.id)

            DB.session.add(db_tweet)
    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e

    else:
        # save the changes to the DB
        DB.session.commit()


nlp = spacy.load('./my_model/')


# We have the same tool we used in the flask shell
def vectorize_tweet(tweet_text):
    'Give the function some text and it returns the word embedding'
    return nlp(tweet_text).vector
