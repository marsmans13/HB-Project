from jinja2 import StrictUndefined
import requests
import json
import xml.etree.ElementTree
from mygpoclient import public
from flask import (Flask, render_template, redirect, request,
                   flash, session, jsonify, abort, g)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
from model import (connect_to_db, db, User, Playlist, Track,
                   TrackPlaylist, Friendship)
import flask_login
from flask_uploads import UploadSet, configure_uploads, IMAGES
import os


app = Flask(__name__)
app.secret_key = "MySecretKey"
app.jinja_env.undefined = StrictUndefined


#---------------------------FLASK-LOGIN-------------------------------

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


photos = UploadSet('photos', IMAGES)

app.config['UPLOADED_PHOTOS_DEST'] = 'static/images'
configure_uploads(app, photos)
    

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
    user = User(username=request.form.get('username'),
                password=request.form.get('password'),
                email=request.form.get('email'),
                fname=request.form.get('fname'),
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
    session.pop('username')
    return redirect('/login')


@app.before_request
def before_request():
    g.user = flask_login.current_user


@app.route("/")
def show_login():
    """ Show login page. """

    if session.get('username'):
        return redirect('/user')

    return render_template("homepage.html")


def show_playlists():
    """ Show a list of all the user's playlists. """

    username = session.get('username')
    user = User.query.filter_by(username=username).first()
    playlists = []

    user_id = user.user_id
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    return playlists


@app.route("/user")
@flask_login.login_required
def show_profile():
    """ Show user's profile page. """

    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    friends = []
    for friend in user.friends:
        friends.append(User.query.filter_by(user_id=friend.user_two_id).first())

    playlists = show_playlists()

    return render_template("user_profile.html",
                            user=user,
                            playlists=playlists,
                            friends=friends)


@app.route('/upload', methods=['POST', 'GET'])
@flask_login.login_required
def upload_photo():
    """ Update user's profile image. """

    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if request.method == 'POST' and 'photo' in request.files:
        filename = photos.save(request.files['photo'])

        image_name = username + "-" + filename
        os.rename('static/images/{}'.format(filename), 'static/images/{}'.format(image_name))

        user.image = image_name
        db.session.commit()

        flash("Photo uploaded successfully.")

    return redirect('/user')


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
    search_list = search_input.split()
    search_terms = "+".join(search_list)

    # -------------------ITUNES REQUEST--------------------------

    response = get_podcasts(search_terms)

    results = response['results']

    # Parse xml file returned to retrieve individual track info
    for result in results:
        if (result.get('feedUrl')):
            xml_url = result['feedUrl']
            doc = requests.get(xml_url)

            if doc.text:
                root = xml.etree.ElementTree.fromstring(doc.text)[0]

                enclosures = []
                titles = []
                elems = []

                for item in root.findall('item'):
                    enclosures.extend(item.findall('enclosure'))
                    titles.extend(item.findall('title'))

                count = 0
                if (len(titles)==len(enclosures)):
                    for i in range(len(titles)):
                        count += 1
                        elems.append((enclosures[i].attrib['url'], titles[i].text, count))

                src_lst = []

                for enclosure in enclosures:
                    audio_src = enclosure.attrib['url']

                result['elements'] = elems
            else:
                results = []

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
@flask_login.login_required
def add_new_playlist():
    """ Add a new playlist. """

    title = request.form.get("playlist-name")
    username = session.get('username')

    user = User.query.filter_by(username=username).first()
    user_id = user.user_id

    playlist = Playlist(user_id=user_id, title=title)

    db.session.add(playlist)
    db.session.commit()

    playlists = Playlist.query.filter_by(user_id=user_id).all()
    flash("Playlist added.")

    return redirect("/user")


@app.route("/add-track", methods=['POST'])
@flask_login.login_required
def add_track():
    """ Add a track to the user's chosen playlist and creates track-playlist relationship. """

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


@app.route("/delete-playlist", methods=['POST'])
@flask_login.login_required
def delete_playlist():
    """ Allow users to delete a playlist. """

    playlist_id = request.form.get("playlist_id")

    playlist = Playlist.query.filter_by(playlist_id=playlist_id).first()
    track_playlists = TrackPlaylist.query.filter_by(playlist_id=playlist_id).all()

    for tp in track_playlists:
        db.session.delete(tp)

    db.session.commit()

    db.session.delete(playlist)
    db.session.commit()

    return redirect("/user")


@app.route("/delete-track", methods=['POST'])
@flask_login.login_required
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
@flask_login.login_required
def search_users():
    """ Search users in database by username. """

    friend_username = request.args.get("search-friends")
    users = User.query.filter(User.username.like('%{}%'.format(friend_username))).all()

    if users:
        return render_template("/search_users.html", users=users)

    flash("No users with that username.")
    return redirect("/user")


@app.route("/add-friend", methods=['POST'])
@flask_login.login_required
def add_friend():
    """ Add friend. """

    friend_username = request.form.get("username")
    friend = User.query.filter_by(username=friend_username).first()
    user_username = session.get('username')

    user_one = User.query.filter_by(username=user_username).first()
    user_id = user_one.user_id

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

    username = session.get('username')
    user = User.query.filter_by(username=username).first()

    if friend.user_id == user.user_id:
        return redirect('/user')

    playlists = []

    if friend.playlists:
        playlists = friend.playlists

    friend_objects = friend.friends
    friend_ids = []

    for friend_obj in friend_objects:
        friend_ids.append(friend_obj.user_two_id)

    friends = []

    for f_id in friend_ids:
        friend_obj = User.query.filter_by(user_id=f_id).first()
        friends.append(friend_obj) 

    if friend:
        return render_template("friend_profile.html", friend=friend,
                                playlists=playlists, friends=friends)
    else:
        flash("Page not available.")
        return redirect("/")


@app.route("/events")
@flask_login.login_required
def show_search_events():

    username = session['username']

    user = User.query.filter_by(username=username).first()

    playlists = []

    if user:
        user_id = user.user_id
        playlists = Playlist.query.filter_by(user_id=user_id).all()

    artists = []

    for playlist in playlists:
        for track in playlist.tracks:
            if track.artist not in artists:
                artists.append(track.artist)

    events = []

    return render_template("event_search.html", artists=artists, events=events)


def get_events(location, search_input):

    search_list = search_input.split()
    search_terms = "+".join(search_list)

    from eventbrite import Eventbrite
    eventbrite = Eventbrite('YHXAIYNKIL7WNRQDO4LX')

    data = {
        'location.address': location,
        'q': search_terms,
    }
    
    events = eventbrite.get('/events/search/', data=data)

    return events


@app.route("/search-events")
@flask_login.login_required
def search_events():
    """ Use Eventbrite API to search events related to user's podcasts. """

    location = request.args.get("location")
    search_input = request.args.get("search-terms")

    events = get_events(location, search_input)

    if events.get('events'):
        events = events['events']
        if len(events) > 10:
            events = events[:10]
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

