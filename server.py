from jinja2 import StrictUndefined
import requests
import json
import xml.etree.ElementTree
from mygpoclient import public
from flask import (Flask, render_template, redirect,
				   request, flash, session, jsonify, abort, g)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from model import (connect_to_db, db,
				   User, Playlist, Track, TrackPlaylist, Friendship)
import flask_login


app = Flask(__name__)

app.secret_key = "MySecretKey"

# Tell Jinja2 to raise an error for undefined variable use.
app.jinja_env.undefined = StrictUndefined


#---------------------FLASK-LOGIN----------------------

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
    

@login_manager.user_loader
def load_user(user_id):

	return User.query.get(int(user_id))


@login_manager.request_loader
def request_loader(request):

	username = request.form.get('username')
	my_user = User.query.filter_by(username=username).first()

	if not my_user:
		return

	user = FlaskUser()
	user.id = username

	user.is_authenticated = request.form.get('password') == my_user.password

	return user


@app.route('/registration', methods=['GET', 'POST'])
def register():

	if request.method == 'GET':
		return render_template('registration_form.html')
	user = User(username=request.form.get('username'), password=request.form.get('password'),
				email=request.form.get('email'), fname=request.form.get('fname'),
				lname=request.form.get('lname'))
	db.session.add(user)
	db.session.commit()
	flash('Registration successful.')
	return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():

	if request.method == 'GET':
		return render_template('homepage.html')

	username = request.form.get('username')
	password = request.form.get('password')
	user = User.query.filter_by(username=username, password=password).first()

	if user is None:
		flash('Username or password is invalid.')
		return redirect('/login')

	session['username'] = username

	flask_login.login_user(user)
	flash('Logged in.')
	return redirect(request.args.get('next') or '/user')


@app.route('/protected')
@flask_login.login_required
def protected():
	return 'Logged in as: {}'.format(flask_login.current_user.username)


@app.route('/logout')
def logout():
	flask_login.logout_user()
	return redirect('/login')

@app.before_request
def before_request():
    g.user = flask_login.current_user

# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'


	# form = LoginForm()
	# if form.validate_on_submit():
	# 	login_user(user)

	# 	flash('Logged in.')

	# 	next = request.args.get('next')
	# 	if not is_safe_url(next):
	# 		return abort(400)

	# 	return redirect(next or '/user')
	# return render_template('homepage.html', form=form)


@app.route("/")
def show_login():
	""" Show login page. """

	return render_template("homepage.html")


def show_playlists():
	""" Show a list of all the user's playlists. """

	username = session.get('username')
	user = User.query.filter_by(username=username).first()
	playlists = []

	if user:
		user_id = user.user_id
		playlists = Playlist.query.filter_by(user_id=user_id).all()

	return playlists


# @app.route("/playlists.json")
# def json_playlists():
# 	""" Show a list of all the user's playlists. """

# 	username = session['username']
# 	user = User.query.filter_by(username=username).first()
# 	playlists = []

# 	if user:
# 		user_id = user.user_id
# 		playlist_objects = Playlist.query.filter_by(user_id=user_id).all()

# 	for obj in playlist_objects:
# 		playlist = {}
# 		playlist['title'] = obj.title
# 		playists.append(playlist)

# 	return jsonify(playlists)


@app.route("/user")
@flask_login.login_required
def show_profile(username='user'):
	""" Show user's profile page. """

	username = session.get('username')
	# if not username:
	# 	flash("You are not logged in")
	# 	return redirect("/")

	playlists = []
	friends = []

	user = User.query.filter_by(username=username).first()

	user_join = db.session.query(User).options(joinedload(User.friends)).all()

	if user:
		user_id = user.user_id
		friend_objects = user.friends
		# returns friendship obj:
		# <Friendship friendship_id="f_id" user_one_id="user_id" user_two_id="friend_id">

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


def get_podcasts(search_terms):
	""" Make request to iTunes and return result. """

	payload = {
		'term': search_terms,
		'limit': 5,
		'entity': 'podcast',
		'kind': 'podcast-episode'
	}

	response = requests.get('https://itunes.apple.com/search',
							params=payload).json()

	return response


@app.route("/search")
@flask_login.login_required
def search_podcasts():
	""" Search podcasts by name/keyword. """

	search_input = request.args.get('q')
	search_list = [term for term in search_input]
	search_terms = "+".join(search_list)

	# -------------------ITUNES REQUEST--------------------------

	# payload = {
	# 	'term': search_terms,
	# 	'limit': 5,
	# 	'entity': 'podcast',
	# 	'kind': 'podcast-episode'
	# }

	# response = requests.get('https://itunes.apple.com/search',
	# 						params=payload).json()

	response = get_podcasts(search_terms)

	results = response['results']

	# Parse xml file returned to retrieve individual track info
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
							playlists=playlists)


@app.route("/top-podcasts")
@flask_login.login_required
def get_top_rated():
	""" Returns a list of the 50 top podcasts and number of subscribers. """

	client = public.PublicClient()

	top_podcasts = {}

	if client.get_toplist():
		toplist_results = client.get_toplist()
		for index, entry in enumerate(toplist_results):
			top_podcasts[(index + 1)] = [entry.title, entry.mygpo_link]

	return render_template("top_podcasts.html", top_podcasts=top_podcasts)


@app.route("/add-playlist", methods=['POST'])
def add_new_playlist():
	""" Add a new playlist. """

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


# @app.route("/pick-playlist")
# def pick_playlist():
# 	""" Gets which playlist the user wants to add a track to. """

# 	playlist_title = request.args.get("playlist")

# 	return playlist_title


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

	# playlist_title = pick_playlist()

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
@flask_login.login_required
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


@app.route("/search-events-form")
def show_search_events():

	username = session['username']

	user = User.query.filter_by(username=username).first()

	playlists = []

	if user:
		user_id = user.user_id
		playlists = Playlist.query.filter_by(user_id=user_id).all()

	artists = []

	if playlists:
		for playlist in playlists:
			for track in playlist.tracks:
				if track.artist not in artists:
					artists.append(track.artist)

	print(artists)

	events = []

	return render_template("event_search.html", artists=artists, events=events)

@app.route("/search-events")
@flask_login.login_required
def search_events():
	""" Use Eventbrite API to search events related to user's podcasts. """

	location = request.args.get("location")
	print(location)
	search_input = request.args.get("search-terms")

	search_list = search_input.split()
	search_terms = "+".join(search_list)

	from eventbrite import Eventbrite

	eventbrite = Eventbrite('YHXAIYNKIL7WNRQDO4LX')

	data = {
		'location.address': location,
		'q': search_terms,
	}

	events = eventbrite.get('/events/search/', data=data)

	# events = eventbrite.get_event('/search?q={}&location.address={}'.format(search_terms, location))

	if events.get('events'):
		events = events['events']
	else:
		events = []

	artists = []

	return render_template("event_search.html", events=events, artists=artists)

if __name__ == "__main__":
	# set to true to use DebugToolbar
	app.debug = True
	# make sure templates, etc. are not cached in debug mode
	app.jinja_env.auto_reload = app.debug

	connect_to_db(app)

	# Use the DebugToolbar
	DebugToolbarExtension(app)

	app.run(port=5000, host='0.0.0.0')

