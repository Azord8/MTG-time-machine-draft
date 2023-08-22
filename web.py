# app.py
from flask import Flask, request, session, render_template
from flask_assets import Environment, Bundle
from requests_oauthlib import OAuth2Session
# from os import pip
import os
from app import main
import json

app = Flask(__name__)
assets = Environment(app)
assets.url = app.static_url_path
scss = Bundle('scss/style.scss', output='css/all.css', filters='libsass,cssmin')
assets.register('scss_all', scss)
# Settings for your app
base_discord_api_url = 'https://discordapp.com/api'
if 'client_id' in os.environ:
    client_id = os.environ['client_id']   # Get from https://discordapp.com/developers/applications
else:
    client_id = "127.0.0.1"
if 'client_secret' in os.environ:
    client_secret = os.environ['client_secret']
redirect_uri = 'https://mtg-time-machine-draft.herokuapp.com/oauth_callback'
scope = ['identify']
token_url = 'https://discordapp.com/api/oauth2/token'
authorize_url = 'https://discordapp.com/api/oauth2/authorize'
app.secret_key = os.urandom(24)
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# A welcome message to test our server
@app.route('/')
def index():
    return "<h1>Welcome to our server !!</h1>"


@app.route('/setup')
def setup():
    test = main.check_setup()
    return "<h1>" + test + "</h1>"


@app.route('/booster')
def booster():
    # TODO Ajax call
    dir_path = os.path.dirname(os.path.realpath(__file__))
    os.chdir(dir_path)
    f = open('config.json', "r")
    config = json.load(f)
    if client_id != "127.0.0.1":
        discord = OAuth2Session(client_id, token=session['discord_token'])
        response = discord.get(base_discord_api_url + '/users/@me')
        return render_template('booster.html', sets=main.find_boosters(config['Date']), id=response.json()['id'])
    else:
        return render_template('booster.html', sets=main.find_boosters(config['Date']))


@app.route('/Ajax-handler')
def ajax():
    action = request.args['action']
    if action == 'get_booster':
        return json.dumps(main.create_booster(request.args['setcode']))
    elif action == 'create_group':
        return json.dumps(main.first_time_user(request.args['id']))
    elif action == 'join_group':
        return json.dumps(main.join_group(request.args['id'], request.args['groupID']))
    if action == 'save_cards':
        cards = request.args['cards']
        transaction = {"Cards": json.loads(cards)}
        return main.create_transaction(request.args['id'], request.args['groupID'], transaction)
    if action == 'save_points':
        transaction = {"Points": request.args['points']}
        return main.create_transaction(request.args['id'], request.args['groupID'], transaction)
    return "test"


@app.route('/Ajax-tester')
def test():
    return render_template('Ajax-tester.html')


@app.route("/login")
def home():
    """
    Presents the 'Login with Discord' link
    """
    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scope)
    login_url, state = oauth.authorization_url(authorize_url)
    session['state'] = state
    print("Login url: %s" % login_url)
    return '<a href="' + login_url + '">Login with Discord</a>'


@app.route("/oauth_callback")
def oauth_callback():
    """
    The callback we specified in our app.
    Processes the code given to us by Discord and sends it back
    to Discord requesting a temporary access token so we can
    make requests on behalf (as if we were) the user.
    e.g. https://discordapp.com/api/users/@me
    The token is stored in a session variable, so it can
    be reused across separate web requests.
    """
    discord = OAuth2Session(client_id, redirect_uri=redirect_uri, state=session['state'], scope=scope)
    token = discord.fetch_token(
        token_url,
        client_secret=client_secret,
        authorization_response=request.url,
    )
    session['discord_token'] = token
    return 'Thanks for granting us authorization. ' \
           'We are logging you in! You can now visit <a href="/profile">/profile</a>'


@app.route("/profile")
def profile():
    """
    Example profile page to demonstrate how to pull the user information
    once we have a valid access token after all OAuth negotiation.
    """
    discord = OAuth2Session(client_id, token=session['discord_token'])
    response = discord.get(base_discord_api_url + '/users/@me')
    # https://discordapp.com/developers/docs/resources/user#user-object-user-structure
    # return 'Profile: %s' % response.json()['id']
    return render_template('profile.html', id=response.json()['id'])


if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    # works for heroku, but I'm moving to AWS
    # app.run(threaded=True, host='0.0.0.0',  port=environ.get('PORT', 5000))
    app.run(threaded=True, host='0.0.0.0', port=5000)
