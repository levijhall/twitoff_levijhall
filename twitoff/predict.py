from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import numpy as np
from .models import User
from .twitter import vectorize_tweet


def build_model(user0_username, user1_username):
    # Grab the users from the DB
    user0 = User.query.filter(User.username == user0_username).one()
    user1 = User.query.filter(User.username == user1_username).one()

    # Get the word embeddings from each user
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # split the user data for training and testing
    user0_vects_train, user0_vects_test = train_test_split(user0_vects,
                                                           test_size=0.2,
                                                           random_state=0)
    user1_vects_train, user1_vects_test = train_test_split(user1_vects,
                                                           test_size=0.2,
                                                           random_state=0)

    # vertically stack the two 2D numpy arrays to make our X matrix
    X_train = np.vstack([user0_vects_train, user1_vects_train])
    X_test = np.vstack([user0_vects_test, user1_vects_test])

    # concatenate our labels of 0 or 1 for each tweet
    zeros_train = np.zeros(user0_vects_train.shape[0])
    ones_train = np.ones(user1_vects_train.shape[0])

    y_train = np.concatenate([zeros_train, ones_train])

    zeros_test = np.zeros(user0_vects_test.shape[0])
    ones_test = np.ones(user1_vects_test.shape[0])

    y_test = np.concatenate([zeros_test, ones_test])

    # instantiate and fit a logistic regression model
    log_reg = LogisticRegression().fit(X_train, y_train)

    # test the accuracy and precision of the model
    p_test = log_reg.predict(X_test)
    confusion = confusion_matrix(y_test, p_test)

    return log_reg, confusion


def predict_user(model, hypo_tweet_text):
    # vectorize the hypothetical tweet text
    # mayke sure it's held in a 2D numpy array
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1, -1)

    return model.predict_proba(hypo_tweet_vect)
