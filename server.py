from jinja2 import StrictUndefined
import requests
import json
import xml.etree.ElementTree
from mygpoclient import public

from flask import (Flask, render_template, redirect, request, flash, session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload

from model import (connect_to_db, db,
				   User, Playlist, Track, TrackPlaylist, Friendship)


app = Flask(__name__)

app.secret_key = "MySecretKey"

# Tell Jinja2 to raise an error for undefined variable use.
app.jinja_env.undefined = StrictUndefined


@app.route("/")
def show_login():
	""" Show login page. """

	if session.get("username"):
		return redirect("/user")

	return render_template("homepage.html")


@app.route("/login", methods=['POST'])
def do_login():
	""" Check login info and either perform login or flash error message. """

	username = request.form.get('username')
	password = request.form.get('password')

	user = User.query.filter(User.username==username).first()

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


@app.route("/logout", methods=['POST'])
def do_logout():
	""" Log the user out. """

	session.pop('username', None)
	session.pop('password', None)

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

	for obj in playlist_objects:
		playlist = {}
		playlist['title'] = obj.title
		playists.append(playlist)

	return jsonify(playlists)


@app.route("/user")
def show_profile(username='user'):
	""" Show user's profile page. """

	username = session.get('username')
	if not username:
		flash("You are not logged in")
		return redirect("/")

	playlists = []
	friends = []

	# print(user_join)

	user = User.query.filter_by(username=username).first()

	user_join = db.session.query(User).options(joinedload(User.friends)).all()

	# user_join = db.session.query(User).options(joinedload(User.friends)).filter_by(user_one_id=current_user).all()

	if user:
		user_id = user.user_id
		friend_objects = user.friends
		# returns friendship obj:
		# <Friendship friendship_id="f_id" user_one_id="user_id" user_two_id="friend_id">

		# friendship_objects = Friendship.query.filter_by(user_one_id=user_id).all()
		friend_ids = []

		for friend in friend_objects:
			friend_ids.append(friend.user_two_id)

		friends = []

		for f_id in friend_ids:
			friend = User.query.filter_by(user_id=f_id).first()
			friends.append(friend)

	if show_playlists():
		playlists = show_playlists()

	return render_template("user_profile.html",
							user=user,
							playlists=playlists,
							friends=friends)


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
		'limit': 5,
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

			result['elements'] = elems

	collections = []

	for result in results:
		if result['collectionName'] not in collections:
			collections.append(result['collectionName'])

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

	# --------------------GPODDER REQUEST------------------------

	client = public.PublicClient()

	gpo_objects = client.search_podcasts(search_input)

	gpo_response = []
	titles = []

	for obj in gpo_objects:
		if obj.title not in collections and obj.title not in titles:
			gpo_response.append(obj)
			titles.append(obj.title)

	if show_playlists():
		playlists = show_playlists()
	else:
		playlists = []

	# --------------------GPODDER TRACK REQUEST------------------------

	# for resp in gpo_response:
	# 	xml_url = resp.url
	# 	if requests.get(xml_url):
	# 		doc = requests.get(xml_url)

	# 		root = xml.etree.ElementTree.fromstring(doc.text)

	# 		root = root[0]

	# 		enclosures = []
	# 		titles = []
	# 		elems = []

	# 		for item in root.findall('item'):
	# 			enclosures.extend(item.findall('enclosure'))
	# 			titles.extend(item.findall('title'))

	# 		if (len(titles)==len(enclosures)):
	# 			for i in range(len(titles)):
	# 				elems.append((enclosures[i].attrib['url'], titles[i].text))

	# 		src_lst = []

	# 		for enclosure in enclosures:
	# 			audio_src = enclosure.attrib['url']

	# 		gpo_xml['elements'] = elems

	return render_template("search_results.html",
							results=results,
							gpo_response=gpo_response,
							playlists=playlists)


@app.route("/top-podcasts")
def get_top_rated():
	""" Returns a list of the 50 top podcasts and number of subscribers. """

	client = public.PublicClient()

	toplist_results = client.get_toplist()
	top_podcasts = {}
	for index, entry in enumerate(toplist_results):
		# print("{} (subscribers: {})".format(entry.title, entry.subscribers))
		top_podcasts[(index + 1)] = [entry.title, entry.mygpo_link]

	return render_template("top_podcasts.html", top_podcasts=top_podcasts)


@app.route("/add-playlist", methods=['POST'])
def add_new_playlist():
	""" Add a new playlist. """

	# pop-up that allows user to create new playlist with a name and description
	title = request.form.get("playlist-name")
	description = request.form.get("description")

	username = session.get('username')

	user = User.query.filter_by(username=username).first()
	user_id = user.user_id

	playlist = Playlist(user_id=user_id, title=title)

	db.session.add(playlist)
	db.session.commit()

	playlists = Playlist.query.filter_by(user_id=user_id).all()
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
	print(track)

	new_track = Track.query.filter_by(audio=rss).first()
	track_id = new_track.track_id

	playlist = Playlist.query.filter_by(title=playlist_title).first()
	playlist_id = playlist.playlist_id
	print(playlist)

	track_playlist = TrackPlaylist(track_id=track_id, playlist_id=playlist_id)
	db.session.add(track_playlist)
	db.session.commit()
	print(track_playlist)

	return redirect("/user")


@app.route("/delete-track", methods=['POST'])
def delete_track():
	""" Allow users to delete a track from a playlist. """

	track_id = request.form.get("track_id")

	track = Track.query.filter_by(track_id=track_id).first()
	track_playlist = TrackPlaylist.query.filter_by(track_id=track_id).first()

	db.session.delete(track_playlist)
	db.session.commit()

	db.session.delete(track)
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

	friend_id = request.args.get("friend_id")

	friend = User.query.filter_by(user_id=friend_id).first()

	playlists = []

	if friend.playlists:
		playlists = friend.playlists

	if friend:
		return render_template("friend_profile.html", friend=friend, playlists=playlists)
	else:
		flash("Page not available.")
		return redirect("/")


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

