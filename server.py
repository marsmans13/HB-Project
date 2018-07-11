from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db

app = Flask(__name__)

app.secret_key = "MySecretKey"

# Tell Jinja2 to raise an error for undefined variable use.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def index():
	""" Load index page. """

	return render_template("homepage.html")


@app.route("/registration-form")
def show_registration():
	""" Show registration form for new users. """

	pass


@app.route("/registration-submit")
def do_registration():
	""" Add a new user to the database. """

	pass


@app.route("/login")
def show_login():
	""" Show login page. """

	pass


@app.route("/login-submit")
def do_login():
	""" Check login info and either perform login or flash error message. """

	pass


@app.route("/log-out")
def do_logout():
	""" Log the user out. """

	pass


@app.route("/<username>")
def show_profile(username):
	""" Show user's profile page. """

	username = 'username'

	# playlist title provided by user
	playlist_title = 'stuff'
	# playlist description provided by user
	playlist_description = 'checking widget'

	# track (podcast) id to be added to id list for url
	track_id = '350359306'

	return render_template("user_profile.html",
							username=username,
							playlistTitle=playlist_title,
							playlistDescription=playlist_description,
							trackId=track_id)


@app.route("/search")
def search_podcasts():
	""" Search podcasts by name/keyword. """

	search_input = request.args.get('search')
	search_list = [term for term in search_input]
	search_terms = "+".join(search_list)

	# Request iTunes API response
	# Change limit after testing
	response1 = requests.get('https://itunes.apple.com/search?term={}&limit=5'
							.format(search_terms)).json()

	# Spotify credentials
	client_id = '5167b20260da450eb7020ffe201264c4'
	client_secret = 'CLIENT_SECRET'
	redirect_uri = 'REDIRECT_URI'

	# Request Spotify API response
	response2 = requests.get('').json()


@app.route("/<username>/playlists")
def show_playlists():
	""" Show a list of all the user's playlists. """

	pass


@app.route("/<username>/<playlist_name>")
def show_podcasts_playlist():
	""" Show a list of all the podcasts in a particular playlist. """

	pass


@app.route("/<friend_username>")
def show_friend_profile():
	""" Show profile/playlists of a profile the user is following. """

	pass


@app.route("/user-info")
def show_user_info():
	""" Show user's info. """

	pass


if __name__ == "__main__":
	# set to true to use DebugToolbar
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')

