from flask import Flask,redirect, url_for, session, render_template, request
from flask_dance.contrib.twitter import make_twitter_blueprint, twitter
from flask_login import UserMixin, current_user, LoginManager, login_required, login_user, logout_user
from flask_dance.consumer import oauth_authorized
from datetime import timedelta
from flask_pymongo import PyMongo
from flask_dance.consumer.storage import BaseStorage
from storetoken import FileStorage


app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev'
app.config["MONGO_URI"] = "mongodb+srv://meetdpatel18:meet4074@cluster0-ywz3w.mongodb.net/maindb?retryWrites=true&w=majority"


twitter_blueprint = make_twitter_blueprint(api_key="SHc4zGhsJmpZ2kXOQl59OIOEV", api_secret="vyJbLO79rTWnzibfLwSiljX90hekeoiSaOORLx4C1Anbg55iDJ")

app.register_blueprint(twitter_blueprint,  url_prefix='/twitter_login')

mongo = PyMongo(app)
login_manager = LoginManager(app)
login_manager.init_app(app)

class User(UserMixin):
    
    def __init__(self,userDocument):
        self.user_id = userDocument.get('user_id')
        self.username = userDocument.get('screen_name')

    def get_id(self):
        return (self.user_id)

@login_manager.user_loader
def load_user(user_id):
    # print(user_id)
    users = mongo.db.users

    print("The users collection is ::", users)
    print(users.find_one({'user_id': user_id}))

    userdata = users.find_one({'user_id': user_id})
    obj = User(userdata)
    return obj

    

# @app.route('/')
# def index():
#     if 'username' in session:
#         return 'You are logged in as ' + session['username']

#     return render_template('index.html')
    
# @app.route('/login', methods=['POST'])
# def login():
#     users = mongo.db.users
#     login_user = users.find_one({'name' : request.form['username']})

#     if login_user:
#         if request.form['pass']== login_user['password']:
#             session['username'] = request.form['username']
#             return redirect(url_for('index'))

#     return 'Invalid username/password combination'


# @app.route('/register', methods=['POST', 'GET'])
# def register():
#     if request.method == 'POST':
#         users = mongo.db.users
#         existing_user = users.find_one({'name' : request.form['username']})

#         if existing_user is None:
#             users.insert({'name' : request.form['username'], 'password' : request.form['pass']})
#             session['username'] = request.form['username']
#             return redirect(url_for('index'))
        
#         return 'That username already exists!'

#     return render_template('register.html')

@app.route('/twitter')
def twitter_login():
    # print(twitter.authorized)
    # if not twitter.authorized:
    #     return redirect(url_for('twitter.login'))
    return redirect(url_for('twitter.login'))
    account_info = twitter.get('account/settings.json')
    account_info_json = account_info.json()
    return '<h1>Your Twitter name is @{}</h1>'.format(account_info_json['screen_name'])

@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    account_info = blueprint.session.get("account/settings.json")
    if account_info.ok:
        account_info_json = account_info.json()
        username = account_info_json['screen_name']

        dict_token = dict(token)
        tweet_tokens = mongo.db.tokens
        users = mongo.db.users
        user = tweet_tokens.find_one({'screen_name':username})
        user_id = dict_token.get('user_id')

        if user is None:
            users.insert({'user_id' : user_id, 'username': username})
            tweet_tokens.insert(dict_token)
            user = {
                'user_id' : dict_token.get('user_id'),
                'screen_name': username,
                }
        
        userObject = User(user)
        

        login_user(userObject)

@app.route('/')
@login_required
def index():
    return '<h1>You are logged in as :{}'.format(current_user.username)

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)