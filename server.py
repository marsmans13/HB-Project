from jinja2 import StrictUndefined
import requests
import json
import xml.etree.ElementTree

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy

from model import (connect_to_db, db,
				   User, Playlist, Track, TrackPlaylist, Friendship)


app = Flask(__name__)

app.secret_key = "MySecretKey"

# Tell Jinja2 to raise an error for undefined variable use.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def show_login():
	""" Show login page. """

	return render_template("homepage.html")


# @app.route("/home")
# def index():
#   """ Load index page. """

#   if session.get('username'):
#       return redirect('/user')

#   return render_template("homepage.html")


@app.route("/login", methods=['POST'])
def do_login():
	""" Check login info and either perform login or flash error message. """

	username = request.form.get('username')
	password = request.form.get('password')

	user = User.query.filter(User.username==username).first()

	print(user)

	if user:
		if user.password == password:
			session['username'] = username
			flash("Logged in.")
			return redirect("/user")
		else:
			flash("Password incorrect.")
			return redirect("/")

	else:
		flash("Username not recognized.")
		return redirect("/")


	session['username'] = username

	return redirect("/user")


@app.route("/logout", methods=['POST'])
def do_logout():
	""" Log the user out. """

	session.pop('username', None)
	session.pop('password', None)
	session.pop('token', None)

	return redirect("/")


@app.route("/registration")
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

	# set_val_user_id()

	user = User(email=email, username=username, password=password,
				fname=fname, lname=lname)

	db.session.add(user)

	db.session.commit()

	return redirect("/user")


@app.route("/playlists")
def show_playlists():
	""" Show a list of all the user's playlists. """

	username = session['username']
	user = User.query.filter_by(username=username).first()
	playlists = []

	if user:
		user_id = user.user_id
		playlists = Playlist.query.filter_by(user_id=user_id).all()

	return playlists


@app.route("/playlists.json")
def json_playlists():
	""" Show a list of all the user's playlists. """

	username = session['username']
	user = User.query.filter_by(username=username).first()
	playlists = []

	if user:
		user_id = user.user_id
		playlist_objects = Playlist.query.filter_by(user_id=user_id).all()
	print(playlist_objects)


	for obj in playlist_objects:
		print(obj.title)
		playlist = {}
		playlist['title'] = obj.title
		playists.append(playlist)

	print(playlists)

	return jsonify(playlists)


@app.route("/user")
def show_profile(username='user'):
	""" Show user's profile page. """

	username = session.get('username')
	playlists = []
	friends = []

	# user_join = db.session.query(User).options(joinedload(User.friends)).filter_by(username=username).all()

	# print(user_join)

	user = User.query.filter_by(username=username).first()
	if user:
		user_id = user.user_id
		friend_objects = user.friends
		# returns friendship obj:
		# <Friendship friendship_id="f_id" user_one_id="user_id" user_two_id="friend_id">

		# friendship_objects = Friendship.query.filter_by(user_one_id=user_id).all()
		friend_ids = []

		for friend in friend_objects:
			friend_ids.append(friend.user_two_id)
		print(friend_ids)

	if show_playlists():
		playlists = show_playlists()

	return render_template("user_profile.html",
							username=username,
							playlists=playlists,
							friends=friend_ids)


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

	for result in results:
		if (result.get('feedUrl')):
			xml_url = result['feedUrl']
			doc = requests.get(xml_url)

			root = xml.etree.ElementTree.fromstring(doc.text)

			root = root[0]

			enclosures = []
			titles = []
			elems = []

			for item in root.findall('item'):
				enclosures.extend(item.findall('enclosure'))
				titles.extend(item.findall('title'))

			if (len(titles)==len(enclosures)):
				for i in range(len(titles)):
					elems.append((enclosures[i].attrib['url'], titles[i].text))

			src_lst = []

			for enclosure in enclosures:
				audio_src = enclosure.attrib['url']

			# print(enclosures)
			# print(titles)
			# print(elems)

			result['elements'] = elems


	# --------------------SPOTIFY REQUEST------------------------


	# sp_response = []

	# payload = {
	# 	'q': search_input,
	# 	'limit': 20,
	# 	'type': 'track'
	# }

	# if session.get('token'):
	# 	headers = {"Authorization":"Bearer {}".format(session['token'])}

	# 	sp_response = requests.get('https://api.spotify.com/v1/search',
	# 								params=payload, headers=headers).json()

	# 	if sp_response.get('tracks'):
	# 		sp_response = sp_response['tracks']['items']
	# 	else:
	# 		sp_reponse = []

	# print(sp_response)

	if show_playlists():
		playlists = show_playlists()
	else:
		playlists = []

	return render_template("search_results.html", results=results, playlists=playlists)


@app.route("/add-playlist", methods=['POST'])
def add_new_playlist():
	""" Add a new playlist. """
	# pop-up that allows user to create new playlist with a name and description
	title = request.form.get("playlist-name")
	description = request.form.get("description")

	username = session.get('username')

	# set_val_playlist_id()

	user = User.query.filter_by(username=username).first()
	user_id = user.user_id

	playlist = Playlist(user_id=user_id, title=title)

	db.session.add(playlist)
	db.session.commit()

	playlists = Playlist.query.filter_by(user_id=user_id).all()

	session['playlists'] = [{'title': playlist.title, 'playlist_id': playlist.playlist_id} for playlist in playlists]
	flash("Playlist added")

	return redirect("/user")


@app.route("/add-track", methods=['POST'])
def add_track():
	""" Add a track to the user's chosen playlist and creates track-playlist relationship. """

	# When the user clicks a track to add to their playlist
	# create a new track obj, and create the track_playlist relationship
	# with the playlist they choose to add the track to

	artist = request.form.get("artist")
	title = request.form.get("title")
	rss = request.form.get("rss")

	playlist_title = request.form.get("playlist")

	track = Track(artist=artist, title=title, audio=rss)
	db.session.add(track)
	db.session.commit()

	new_track = Track.query.filter_by(audio=rss).first()
	track_id = new_track.track_id

	playlist = Playlist.query.filter_by(title=playlist_title).first()
	playlist_id = playlist.playlist_id

	track_playlist = TrackPlaylist(track_id=track_id, playlist_id=playlist_id)
	db.session.add(track_playlist)
	db.session.commit()

	return redirect("/user")


# @app.route("/user/<playlist_name>")
# def show_podcasts_playlist(username, playlist_name):
#   """ Show a list of all the podcasts in a particular playlist. """

#   pass

@app.route("/search-users")
def search_users():
	""" Search users in database by username. """

	search_username = request.args.get("search-friends")

	users = User.query.filter(User.username.like('%{}%'.format(search_username))).all()

	if users:
		return render_template("/search_users.html", users=users)

	flash("No users with that username.")
	return redirect("/user")


@app.route("/add-friend", methods=['POST'])
def add_friend():
	""" Add friend. """

	friend_username = request.form.get("username")

	friend = User.query.filter_by(username=friend_username).first()
	print(friend)

	user_username = session.get('username')

	if user_username:
		user_one = User.query.filter_by(username=user_username).first()
		user_id = user_one.user_id
	else:
		flash("You must be logged in to view this page.")
		return redirect("/")

	if friend:
		friend_id = friend.user_id
		new_friend = Friendship(user_one_id=user_id, user_two_id=friend_id)
		db.session.add(new_friend)
		db.session.commit()
		flash("Friend added.")
	else:
		flash("Friend not successfully added.")
	return redirect("/user")


@app.route("/friend")
def show_friend_profile():
	""" Show profile/playlists of a profile the user is following. """

	pass


@app.route("/user-info")
def show_user_info():
	""" Show user's info. """

	pass


# def set_val_user_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(User.user_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('users_user_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


# def set_val_playlist_id():
#     """Set value for the next user_id after seeding database"""

#     # Get the Max user_id in the database
#     result = db.session.query(func.max(Playlist.playlist_id)).one()
#     max_id = int(result[0])

#     # Set the value for the next user_id to be max_id + 1
#     query = "SELECT setval('playlists_playlist_id_seq', :new_id)"
#     db.session.execute(query, {'new_id': max_id + 1})
#     db.session.commit()


if __name__ == "__main__":
	# set to true to use DebugToolbar
	app.debug = True
	# make sure templates, etc. are not cached in debug mode
	app.jinja_env.auto_reload = app.debug

	connect_to_db(app)

	# Use the DebugToolbar
	DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')

