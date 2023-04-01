from flask import Flask, render_template, request, send_file

from seaborn import heatmap
from matplotlib.figure import Figure

from .models import DB, User
from .twitter import add_or_update_user
from .predict import predict_user, build_model
from .utility import nocache, fig_response


def create_app():
    app = Flask(__name__)

    # database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # register our database with the app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template('base.html', title='Home', users=users)

    @app.route('/reset')
    def reset():
        # Drop all database tables
        DB.drop_all()
        # Recreate all database tables according to the
        # indicated schema in models.py
        DB.create_all()
        return render_template('base.html', title='Reset Database')

    @app.route('/update')
    def update():
        # get list of usernames of all users
        users = User.query.all()
        # usernames = []
        # for user in users:
        #     usernames.append(user.username)

        for username in [user.username for user in users]:
            add_or_update_user(username)

        return render_template('base.html', title='Users Updated', users=users)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):
        if username is None:
            username = request.values['user_name']

        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User "{username}" has been successfully added!'

            tweets = User.query.filter(User.username == username).one().tweets
        except Exception as e:
            message = f'Error adding {username}: {e}'
            tweets = []
            # raise e

        return render_template('user.html',
                               title=username,
                               tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user0, user1 = sorted([request.values['user0'],
                               request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compare a user to themselves!'

        else:
            model, cf_matrix = build_model(user0, user1)
            prediction = predict_user(model, hypo_tweet_text)[0]

            values = ','.join(str(v) for v in cf_matrix.flat)

            # 0 if user0, 1 if user1
            if prediction[0] > prediction[1]:
                winner = user1
                loser = user0
                odds = prediction[0] / prediction[1]
            else:
                winner = user0
                loser = user1
                odds = prediction[1] / prediction[0]

            message = '"{}" is {:.2f} times more likey to be said'\
                      ' by {} than by {}'.format(hypo_tweet_text,
                                                 odds,
                                                 winner,
                                                 loser
                                                 )

        return render_template('prediction.html',
                               title='Prediction',
                               message=message,
                               values=values,
                               user0=user0,
                               user1=user1)

    @app.route('/img/plot.png')
    def plot():
        try:
            values = [int(x) for x in request.args.get('v', '').split(',')]
            name0 = request.args.get('u0', '0')
            name1 = request.args.get('u1', '1')

            if len(values) == 4:
                cf_matrix = [[values[0], values[1]],
                             [values[2], values[3]]]

                print(cf_matrix, name0, name1)
            else:
                raise Exception

        except Exception:
            print("There was a problem with the arguments", request.args)
            return send_file('img/error.png', mimetype='image/png')

        categories = [name0, name1]
        fig = Figure()
        ax = fig.subplots()
        heatmap(cf_matrix,
                annot=True,
                xticklabels=categories,
                yticklabels=categories,
                cmap='Blues',
                ax=ax)
        ax.set_title("Confusion Matrix")
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")

        return nocache(fig_response(fig))

    return app
