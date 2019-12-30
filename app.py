from flask import Flask,redirect, url_for
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, current_user, LoginManager, login_required, login_user, logout_user
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
from flask_dance.consumer import oauth_authorized
from sqlalchemy.orm.exc  import NoResultFound
from datetime import timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///login.db'
# app.config['REMEMBER_COOKIE_DURATION'] = timedelta(seconds=20)

twitter_blueprint = make_twitter_blueprint(api_key="SHc4zGhsJmpZ2kXOQl59OIOEV", api_secret="vyJbLO79rTWnzibfLwSiljX90hekeoiSaOORLx4C1Anbg55iDJ")

app.register_blueprint(twitter_blueprint,  url_prefix='/twitter_login')

db = SQLAlchemy(app)
login_manager = LoginManager(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True)

class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    user = db.relationship(User)

@login_manager.user_loader
def load_user(user_id):
    twitter_blueprint.storage = SQLAlchemyStorage(OAuth,db.session)
    return User.query.get(int(user_id))


@app.route('/twitter')
def twitter_login():
    print(twitter.authorized)
    # if not twitter.authorized:
    #     return redirect(url_for('twitter.login'))
    return redirect(url_for('twitter.login'))
    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()
    return '<h1>Your Twitter name is @{}'.format(account_info_json['screen_name'])

@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    account_info = blueprint.session.get("account/settings.json")
    
    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['screen_name']

        query = User.query.filter_by(username=username)

        try:
            user = query.one()
        except NoResultFound:
            user = User(username=username)
            db.session.add(user)
            db.session.commit()

        login_user(user)

@app.route('/')
@login_required
def index():
    return '<h1>You are logged in as :{}'.format(current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)