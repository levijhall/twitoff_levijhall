# Twitoff

Twitter users go head-to-head to see who would have been more likely to tweet a hypnotical message. Using their most recent tweets, processed through the SpaCy language model, and classified by a logistic curve, we can infer the probability that any text could have been written by any chosen user.

## How to run

1. Create a `pipenv` environment by running
    1. `pipenv install -r requirements.txt`
2. Entire the environment with `pipenv shell`
3. And run `flask --app twitoff run`

The webpage should now be running locally at `http://127.0.0.1:5000`