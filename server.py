from jinja2 import StrictUndefined
import requests
import base64
import json

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

from model import (connect_to_db, db,
				   User, Playlist, Track, TrackPlaylist, Friendship)

from user_auth import auth, callback

app = Flask(__name__)

app.secret_key = "MySecretKey"

# Tell Jinja2 to raise an error for undefined variable use.
app.jinja_env.undefined = StrictUndefined


CLIENT_ID = "5167b20260da450eb7020ffe201264c4"
CLIENT_SECRET = "f0315bd7dd01466290b074d91f93d8f6"

# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://0.0.0.0"
PORT = 5000
REDIRECT_URI = "http://localhost:5000/callback/q"
SCOPE = "playlist-modify-public playlist-modify-private"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "client_id": CLIENT_ID,
    "response_type": "code",
    "scope": SCOPE
}


@app.route("/")
def auth():
    # Auth Step 1: Authorization
    # url_args = requests.get(REDIRECT_URI, params=auth_query_parameters)
    url_args = 'response_type=code&client_id={}&scope={}&redirect_uri={}&show_dialog=true'.format(auth_query_parameters['client_id'],
                                                                                auth_query_parameters['scope'],
                                                                                REDIRECT_URI)
    
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    # auth_token = request.form.get(CLIENT_ID, CLIENT_SECRET)
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"

    auth_token = request.args.get('code')
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    session['username'] = profile_data.get('display_name')
    session['token'] = access_token

    return redirect("/<username>")


# @app.route("/home")
# def index():
# 	""" Load index page. """

# 	if session.get('username'):
# 		return redirect('/<username>')

# 	return render_template("homepage.html")


@app.route("/registration-form")
def show_registration():
	""" Show registration form for new users. """

	return render_template("registration_form.html")


@app.route("/registration-submit", methods=['POST'])
def do_registration():
	""" Add a new user to the database. """

	email = request.form.get("email")
	username = request.form.get("username")
	password = request.form.get("password")
	fname = request.form.get("fname")
	lname = request.form.get("lname")

	session['username'] = username
	flash("Logged in.")

	set_val_user_id()

	user = User(email=email, username=username, password=password,
				fname=fname, lname=lname)

	db.session.add(user)

	db.session.commit()

	return redirect("/<username>")


@app.route("/login")
def show_login():
	""" Show login page. """

	pass


@app.route("/login", methods=['GET', 'POST'])
def login():
	""" Check login info and either perform login or flash error message. """

	username = request.form.get('username')
	password = request.form.get('password')

	session['username'] = username
	flash("Logged in.")

	user = User.query.filter_by(username=username).first()
	print(user)

	return redirect("/<username>")

	# if user:
		# if user.password == password:
		# 	session['username'] = username
		# 	flash("Logged in.")
        	# return redirect("/<username>")

  #       else:
  #       	flash("Password incorrect.")
  		# print("check")

    # else:
    # 	flash("Username not recognized.")


# def user_in_db(username):

#     if User.query.filter_by(username=username).one() is not False:
#         return True

#     return False


@app.route("/logout", methods=['POST'])
def do_logout():
	""" Log the user out. """

	session.pop('username', None)
	session.pop('password', None)
	return redirect("/")


@app.route("/<username>")
def show_profile(username='user'):
	""" Show user's profile page. """

	username = session.get('username')

	# playlist title provided by user
	playlist_title = 'how stuff works'
	# playlist description provided by user
	description = 'wordy description'

	# track (podcast) id to be added to id list for url
	track_id = '350359306'

	return render_template("user_profile.html",
							username=username,
							playlistTitle=playlist_title,
							playlistDescription=description,
							trackId=track_id)


@app.route("/search")
def show_search_form():
	""" Search podcasts by name/keyword. """

	return render_template("search.html")


@app.route("/search-submit")
def search_podcasts():
	""" Search podcasts by name/keyword. """

	# iTunes API requests

	search_input = request.args.get('q')
	search_list = [term for term in search_input]
	search_terms = "+".join(search_list)

	# Change limit after testing

	# -------------------ITUNES REQUEST--------------------------

	payload = {
		'term': search_terms,
		'limit': 10,
		'entity': 'podcast',
		'kind': 'podcast-episode'
	}

	response = requests.get('https://itunes.apple.com/search',
							params=payload).json()

	results = response['results']


	# ----------------SPOTIFY REQUEST WITH SPOTIPY--------------------

	# import spotipy
	# import spotipy.util as util


	# client_id = '5167b20260da450eb7020ffe201264c4'
	# client_secret = 'f0315bd7dd01466290b074d91f93d8f6'
	# redirect_uri = 'https://localhost:5000/search'

	# scope = 'user-library-read'

	# username = '1291159305'

	# token = util.prompt_for_user_token(username, scope)

	# if token:
	#     sp = spotipy.Spotify(auth=token)
	#     results = sp.current_user_saved_tracks()
	#     for item in results['items']:
	#         track = item['track']
	#         print track['name'] + ' - ' + track['artists'][0]['name']
	# 	else:
	#     	print "Can't get token for", username


	# name = 'fresh+air'

	# results = spotify.search(q='artist:' + name, type='artist')
	# items = results['artists']['items']
	# if len(items) > 0:
	#     artist = items[0]
	#     print artist['name'], artist['images'][0]['url']


	# --------------------SPOTIFY REQUEST------------------------

	# send_tokens = requests.post('https://accounts.spotify.com/api/token',
	# 							params=resp_payload)

	payload = {
		'q': search_input,
		'limit': 20,
		'type': 'track'
	}

	headers = {"Authorization":"Bearer {}".format(session['token'])}

	sp_response = requests.get('https://api.spotify.com/v1/search',
								params=payload, headers=headers).json()

	raw = sp_response['tracks']

	if sp_response.get('tracks'):
		sp_response = sp_response['tracks']['items']
	else:
		sp_reponse = []

	return render_template("search_results.html", sp_response=sp_response, results=results, raw=raw)


@app.route("/add-playlist", methods=['POST'])
def add_new_playlist():
	""" Add a new playlist. """
	# pop-up that allows user to create new playlist with a name and description
	title = request.form.get("playlist-name")
	description = request.form.get("description")

	username = session.get('username')

	set_val_playlist_id()

	user = User.query.filter_by(username=username).first()
	user_id = user.user_id

	playlist = Playlist(user_id=user_id, title=title)

	db.session.add(playlist)
	db.session.commit()

	return redirect("/<username>")

@app.route("/<username>/playlists")
def show_playlists(username):
	""" Show a list of all the user's playlists. """

	pass


# @app.route("/<username>/<playlist_name>")
# def show_podcasts_playlist(username, playlist_name):
# 	""" Show a list of all the podcasts in a particular playlist. """

# 	pass


@app.route("/<friend_username>")
def show_friend_profile(friend_username):
	""" Show profile/playlists of a profile the user is following. """

	pass


@app.route("/user-info")
def show_user_info():
	""" Show user's info. """

	pass


def set_val_user_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(User.user_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('users_user_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


def set_val_playlist_id():
    """Set value for the next user_id after seeding database"""

    # Get the Max user_id in the database
    result = db.session.query(func.max(Playlist.playlist_id)).one()
    max_id = int(result[0])

    # Set the value for the next user_id to be max_id + 1
    query = "SELECT setval('playlists_playlist_id_seq', :new_id)"
    db.session.execute(query, {'new_id': max_id + 1})
    db.session.commit()


if __name__ == "__main__":
	# set to true to use DebugToolbar
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

