from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
)
from models import *
from api import *
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)
import os
import matplotlib.pyplot as plt

# import seaborn as sns  # type: ignore

app = Flask(__name__, static_url_path="/static")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///projectdb.sqlite3"
app.config["SECRET_KEY"] = "secret_key"
app.config["UPLOAD_FOLDER_1"] = "static/audios"
app.config["UPLOAD_FOLDER_2"] = "static/posters"
app.config["UPLOAD_FOLDER_3"] = "static/album_posters"
app.config["UPLOAD_FOLDER_4"] = "static/profile_pictures"
plt.switch_backend("Agg")


db.init_app(app)
app.app_context().push()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/", methods=["GET", "POST"])
def index():
    return redirect("/home")


@app.route("/home")
def welcome():
    return render_template("welcome.html")


@app.route("/login", methods=["GET", "POST"])  # type:ignore
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        status = False
        message = ""
        user_list = []
        users = User.query.all()
        for user in users:
            user_list.append(user.username)
        user_name = request.form.get("username")
        password = request.form.get("pass")
        if user_name in user_list:
            this_user = User.query.filter_by(username=user_name).first()
            if password == this_user.password:
                status = True
                login_user(this_user)
            else:
                message = "Invalid username or password!"
        else:
            message = "Username does not exit!"
        if not status:
            return render_template("login.html", message=message)
        else:
            user = User.query.filter_by(username=user_name).first()
            if user.blacklisted:
                return render_template("blacklist_page.html")
            else:
                return redirect(url_for("homepage"))


@app.route("/register", methods=["GET", "POST"])  # type:ignore
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        user_list = []
        message = ""
        users = User.query.all()
        for user in users:
            user_list.append(user.username)
        user_name = request.form.get("r_username")
        pass_word = request.form.get("r_pass")
        name = request.form.get("name").title()  # type: ignore
        if user_name not in user_list:
            profile_pic = request.files["profile_pic"]
            if profile_pic:
                profile_picture = profile_pic.filename
                profile_pic.save(os.path.join(app.config["UPLOAD_FOLDER_4"], profile_picture))  # type: ignore
            else:
                profile_picture = r"default_profile.jpg"
            to_add = User(
                username=user_name,
                password=pass_word,
                name=name,
                profile_pic=profile_picture,
            )
            db.session.add(to_add)
            db.session.commit()
        else:
            message = "User already exits! Try a different username."
            return render_template("register.html", message=message)
        this_user = User.query.filter_by(username=user_name).first()
        login_user(this_user)
        return redirect(url_for("homepage"))


def search(q):
    query = "%" + str(q) + "%"
    songs = Song.query.filter(Song.song_name.like(query)).all()
    artist_song = Song.query.filter(Song.artist.like(query)).all()
    artists = []
    artist_user = []
    for a in artist_song:
        if a.artist not in artists:
            artists.append(a.artist)
    for i in artists:
        user = User.query.filter_by(name=i, user_type="creator").first()
        artist_user.append(user)
    genre_song = Song.query.filter(Song.genre.like(query)).all()
    genres = []
    for g in genre_song:
        if g.genre not in genres:
            genres.append(g.genre)
    albums = Album.query.filter(Album.album_name.like(query)).all()
    return songs, artist_user, albums, genres


@app.route("/homepage", methods=["GET", "POST"])  # type:ignore
@login_required
def homepage():
    if request.method == "GET":
        user_id = current_user.user_id  # type: ignore
        s_list = Song.query.all()
        song_list = s_list.copy()
        songs = []
        a_list = Album.query.all()
        album_list = a_list.copy()
        albums = []
        all_artists = User.query.filter_by(user_type="creator").all()
        art = all_artists.copy()
        artists = []
        if len(song_list) <= 7:
            songs = song_list
        else:
            while len(songs) != 7:
                max_r = 0
                song = ""
                for i in song_list:
                    if int(i.rating) >= max_r:
                        max_r = int(i.rating)
                        song = i
                songs.append(song)
                song_list.remove(song)
        if len(album_list) <= 7:
            albums = album_list
        else:
            while len(albums) != 7:
                max_r = 0
                album = ""
                for i in album_list:
                    if int(i.rating) >= max_r:
                        max_r = int(i.rating)
                        album = i
                albums.append(album)
                album_list.remove(album)
        artists = []
        while len(artists) != len(all_artists):
            max_s = 0
            artist = ""
            for i in art:
                if len(i.songs) >= max_s:
                    max_s = len(i.songs)
                    artist = i
            artists.append(artist)
            art.remove(artist)

        return render_template(
            "homepage.html",
            songs=songs,
            user_id=user_id,
            albums=albums,
            artists=artists[0:7],
        )


@app.route("/listen_song/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def listen_song(song_id):
    if request.method == "GET":
        user = User.query.get(current_user.user_id)  # type: ignore
        status = False
        already_rated = False
        song = Song.query.get(song_id)
        song.played += 1
        path = "../" + song.path
        liked_songs = user.liked_songs
        liked_songs_ids = []
        for liked_song in liked_songs:
            liked_songs_ids.append(liked_song.song_id)
        if song_id in liked_songs_ids:
            status = True
        if song in user.rated_songs:
            already_rated = True
        db.session.commit()
        return render_template(
            "listen_song.html",
            song=song,
            path=path,
            status=status,
            already_rated=already_rated,
        )


@app.route("/like_song/<int:song_id>", methods=["GET", "POST"])  # type:ignore
@login_required
def like_song(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    user.liked_songs.append(Song.query.get(song_id))  # type: ignore
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/unlike_song/<int:song_id>", methods=["GET", "POST"])  # type:ignore
@login_required
def unlike_song(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    user.liked_songs.remove(Song.query.get(song_id))  # type: ignore
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/rate_song1/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def rate_song1(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.rated_songs.append(song)
    if int(song.rating) == 0:
        song.rating = 1
    else:
        song.rating = (song.rating + 1) / 2
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/rate_song2/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def rate_song2(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.rated_songs.append(song)
    if int(song.rating) == 0:
        song.rating = 2
    else:
        song.rating = (song.rating + 2) / 2
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/rate_song3/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def rate_song3(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.rated_songs.append(song)
    if int(song.rating) == 0:
        song.rating = 3
    else:
        song.rating = (song.rating + 3) / 2
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/rate_song4/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def rate_song4(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.rated_songs.append(song)
    if int(song.rating) == 0:
        song.rating = 4
    else:
        song.rating = (song.rating + 4) / 2
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/rate_song5/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def rate_song5(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.rated_songs.append(song)
    if int(song.rating) == 0:
        song.rating = 5
    else:
        song.rating = (song.rating + 5) / 2
    db.session.commit()
    return redirect(url_for("listen_song", song_id=song_id))


@app.route("/all_songs", methods=["GET", "POST"])  # type:ignore
def all_songs():
    if request.method == "GET":
        songs = Song.query.all()
        return render_template("all_songs.html", songs=songs)


@app.route("/all_albums", methods=["GET", "POST"])  # type:ignore
def all_albums():
    if request.method == "GET":
        albums = Album.query.all()
        return render_template("all_albums.html", albums=albums)


@app.route("/all_artists", methods=["GET", "POST"])  # type:ignore
def all_artists():
    if request.method == "GET":
        artists = User.query.filter_by(user_type="creator").all()
        return render_template("all_artists.html", artists=artists)


@app.route("/creator", methods=["GET", "POST"])  # type: ignore
@login_required
def creator():
    user_id = current_user.user_id  # type: ignore
    user = User.query.get(user_id)
    if request.method == "GET":
        songs = user.songs
        albums = user.albums
        ratings = []
        for song in songs:
            ratings.append(song.rating)
        if len(ratings) != 0:
            avg_rating = round(sum(ratings) / len(ratings), 2)
        else:
            avg_rating = 0
        return render_template(
            "creator.html",
            status=user.user_type,
            songs=songs,
            avg_rating=avg_rating,
            albums=albums,
            Album=Album,
        )
    if request.method == "POST":
        user.user_type = "creator"
        db.session.commit()
        return render_template("creator.html", status=user.user_type)


@app.route("/creator_songs", methods=["GET", "POST"])  # type: ignore
@login_required
def creator_songs():
    if request.method == "GET":
        creator_id = current_user.user_id  # type: ignore
        songs = Song.query.filter_by(creator=creator_id).all()
        return render_template("creator_songs.html", songs=songs, Album=Album)


@app.route("/upload_song", methods=["GET", "POST"])  # type: ignore
@login_required
def upload_song():
    creator = User.query.get(current_user.user_id)  # type: ignore
    if request.method == "GET":
        return render_template("upload_song.html")
    if request.method == "POST":
        title = request.form.get("title").title()  # type: ignore
        artist = creator.name
        lyrics = request.form.get("lyrics")
        genre = request.form.get("genre")
        if genre == "Select Genre":
            message = "Please select a valid genre!"
            return render_template("upload_song.html", message=message)
        song = request.files["song"]
        song_name = song.filename
        print(song_name)
        song.save(os.path.join(app.config["UPLOAD_FOLDER_1"], song_name))  # type: ignore
        # song_path = os.path.join(app.config['UPLOAD_FOLDER_1'], song_name)  # type: ignore
        poster = request.files["poster"]
        if poster:
            poster_name = poster.filename
            poster.save(os.path.join(app.config["UPLOAD_FOLDER_2"], poster_name))  # type: ignore
            # poster_path = os.path.join(app.config['UPLOAD_FOLDER_2'], poster_name)  # type: ignore
        else:
            poster_name = r"default poster.jpg"
        print(poster_name)
        creator_id = current_user.user_id  # type: ignore
        add_song = Song(
            song_name=title,
            lyrics=lyrics,
            artist=artist,
            path=song_name,
            poster=poster_name,
            creator=creator_id,
            genre=genre,
        )
        db.session.add(add_song)
        db.session.commit()
        return redirect(url_for("creator_songs"))


@app.route("/update_song/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def update_song(song_id):
    song = Song.query.get(song_id)
    if request.method == "GET":
        return render_template("update_song.html", song=song)
    if request.method == "POST":
        genre = request.form.get("genre")
        if genre == "Select Genre":
            message = "Please select a valid genre!"
            return render_template(
                "update_song.html", message=message, song=Song.query.get(song_id)
            )
        if request.form.get("title") != song.song_name:
            song.song_name = request.form.get("title")
        if request.form.get("artist") != song.artist:
            song.artist = request.form.get("artist")
        if request.form.get("genre") != song.genre:
            song.genre = request.form.get("genre")
        if request.form.get("lyrics") != song.lyrics:
            song.lyrics = request.form.get("lyrics")
        db.session.commit()
        return redirect(url_for("creator_songs"))


@app.route("/delete_song/<int:song_id>", methods=["GET", "POST"])
def delete_song(song_id):
    song = Song.query.get(song_id)
    song_path = os.path.join(app.config["UPLOAD_FOLDER_1"], song.path)
    poster_path = os.path.join(app.config["UPLOAD_FOLDER_2"], song.poster)
    os.remove(song_path)
    os.remove(poster_path)
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for("creator_songs"))


@app.route("/user_playlists/<int:user_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def user_playlist(user_id):
    if request.method == "GET":
        playlists = Playlist.query.filter_by(user=user_id).all()
        return render_template("user_playlists.html", playlists=playlists)


@app.route("/create_playlist", methods=["GET", "POST"])  # type: ignore
@login_required
def create_playlist():
    if request.method == "GET":
        songs = Song.query.all()
        print(songs)
        return render_template("create_playlist.html", songs=songs)
    if request.method == "POST":
        playlist_name = request.form.get("playlist_name")
        user_id = current_user.user_id  # type: ignore
        to_add = Playlist(name=playlist_name, user=user_id)
        db.session.add(to_add)
        db.session.commit()
        song_list = request.form.getlist("songs")
        for song in song_list:
            song_to_add = Song.query.get(int(song))
            to_add.playlist.append(song_to_add)
        db.session.commit()
        return redirect(url_for("user_playlist", user_id=user_id))


@app.route("/playlist_page/<int:playlist_id>/", methods=["GET", "POST"])  # type: ignore
@login_required
def playlist_page(playlist_id):
    if request.method == "GET":
        play_list = Playlist.query.get(playlist_id)
        playlist_songs = play_list.playlist
        return render_template("playlist_page.html", playlist_songs=playlist_songs)


@app.route("/update_playlist/<int:playlist_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def update_playlist(playlist_id):
    play_list = Playlist.query.get(playlist_id)
    if request.method == "GET":
        songs = play_list.playlist
        all_songs = Song.query.all()
        not_in_playlist = []
        for song in all_songs:
            if song not in songs:
                not_in_playlist.append(song)
        return render_template(
            "update_playlist.html",
            songs=songs,
            playlist=play_list,
            not_in_playlist=not_in_playlist,
        )
    if request.method == "POST":
        name = request.form.get("playlist_name")
        song_list = request.form.getlist("songs")
        if name != play_list.name:
            play_list.name = name
        for song in song_list:
            song_to_add = Song.query.get(int(song))
            play_list.playlist.append(song_to_add)
        db.session.commit()
        return redirect(url_for("playlist_page", playlist_id=playlist_id))


@app.route(
    "/delete_playlist_song/<int:song_id>/<int:playlist_id>", methods=["GET", "POST"]
)
def delete_playlist_song(song_id, playlist_id):
    play_list = Playlist.query.get(playlist_id)
    songs = play_list.playlist
    to_remove = Song.query.get(song_id)
    songs.remove(to_remove)
    db.session.commit()
    if Playlist.query.get(playlist_id).playlist == []:
        db.session.delete(Playlist.query.get(playlist_id))
        db.session.commit
    return redirect(url_for("update_playlist", playlist_id=playlist_id))


@app.route("/delete_playlist/<int:playlist_id>", methods=["GET", "POST"])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for("user_playlist", user_id=current_user.user_id))  # type: ignore


@app.route("/liked_songs", methods=["GET", "POST"])  # type: ignore
@login_required
def liked_song():
    user = User.query.get(current_user.user_id)  # type: ignore
    liked_song_list = user.liked_songs
    if request.method == "GET":
        return render_template("liked_songs.html", liked_song_list=liked_song_list)


@app.route("/remove_liked_song/<int:song_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def remove_liked_song(song_id):
    user = User.query.get(current_user.user_id)  # type: ignore
    song = Song.query.get(song_id)
    user.liked_songs.remove(song)
    db.session.commit()
    return redirect(url_for("liked_song"))


@app.route("/creator_albums", methods=["GET", "POST"])
@login_required
def creator_albums():
    creator = User.query.get(current_user.user_id)  # type: ignore
    albums = creator.albums
    artist = creator.name
    return render_template("creator_albums.html", albums=albums, artist=artist)


@app.route("/create_album", methods=["GET", "POST"])  # type: ignore
@login_required
def create_albums():
    creator_songs = Song.query.filter_by(creator=current_user.user_id)  # type: ignore
    songs = []
    for song in creator_songs:
        if song.album is None:
            songs.append(song)
    if request.method == "GET":
        return render_template("create_album.html", songs=songs)
    if request.method == "POST":
        album_name = request.form.get("album_name")
        poster = request.files["poster"]
        poster_name = poster.filename
        poster.save(os.path.join(app.config["UPLOAD_FOLDER_3"], poster_name))  # type: ignore
        # poster_path = os.path.join(app.config['UPLOAD_FOLDER_3'], poster_name) # type: ignore
        song_list = request.form.getlist("songs")
        genre = request.form.get("genre")
        artist = User.query.get(current_user.user_id).name  # type: ignore
        if genre == "Select Genre":
            message = "Please select a valid genre!"
            return render_template("create_album.html", message=message, songs=songs)
        else:
            to_add = Album(album_name=album_name, genre=genre, poster=poster_name, creator=current_user.user_id, rating=0, artist=artist)  # type: ignore
            db.session.add(to_add)
            db.session.commit()
            song_ratings = []
            for song_id in song_list:
                song = Song.query.get(song_id)
                to_add.songs.append(song)
                song_ratings.append(int(song.rating))
            rating = round(sum(song_ratings) / len(song_ratings), 2)
            print(rating)
            to_add.rating = rating
            db.session.commit()
            return redirect(url_for("creator_albums"))


@app.route("/album_page/<int:album_id>", methods=["GET", "POST"])
@login_required
def album_page(album_id):
    album = Album.query.get(album_id)
    return render_template("album_page.html", songs=album.songs, album=album)


@app.route("/update_album/<int:album_id>", methods=["GET", "POST"])  # type: ignore
@login_required
def update_album(album_id):
    creator_songs = Song.query.filter_by(creator=current_user.user_id)  # type: ignore
    not_album_songs = []
    for song in creator_songs:
        if song.album is None:
            not_album_songs.append(song)
    album = Album.query.get(album_id)
    if request.method == "GET":
        return render_template(
            "update_album.html",
            songs=album.songs,
            album=album,
            not_album_songs=not_album_songs,
        )
    if request.method == "POST":
        name = request.form.get("album_name")
        if name != album.album_name:
            album.album_name = name
        add_songs = request.form.getlist("songs")
        for song in add_songs:
            album.songs.append(Song.query.get(song))
        db.session.commit()
        ratings = []
        for song in album.songs:
            ratings.append(int(song.rating))
        album.rating = round(sum(ratings) / len(ratings), 2)
        db.session.commit()
        return redirect(url_for("creator_albums"))


@app.route("/delete_album/<int:album_id>", methods=["GET", "POST"])
def delete_album(album_id):
    album = Album.query.get(album_id)
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for("creator_albums", album_id=album_id))


@app.route("/delete_album_song/<int:album_id>/<int:song_id>", methods=["GET", "POST"])
def delete_album_song(album_id, song_id):
    song = Song.query.get(song_id)
    album = Album.query.get(album_id)
    album.songs.remove(song)
    db.session.commit()
    if Album.query.get(album_id).songs == []:
        db.session.delete(Album.query.get(album_id))
        db.session.commit()
    return redirect(url_for("update_album", album_id=album_id))


@app.route("/artist_page/<int:artist_id>", methods=["GET"])
@login_required
def artist_page(artist_id):
    artist = User.query.get(artist_id)
    songs = artist.songs
    return render_template("artist_page.html", songs=songs, Album=Album)


@app.route("/genre_page/<genre_name>", methods=["GET"])
@login_required
def genre_page(genre_name):
    songs = Song.query.filter_by(genre=genre_name).all()
    return render_template("genre_page.html", songs=songs)


@app.route("/search_page", methods=["POST", "GET"])  # type: ignore
def search_page():
    if request.method == "POST":
        if "query" in request.form:
            query = request.form["query"]
            songs, artists, albums, genres = search(query)
            return render_template(
                "search.html",
                songs=songs,
                artists=artists,
                albums=albums,
                genres=genres,
            )


@app.route("/profile", methods=["GET", "POST"])  # type: ignore
@login_required
def profile():
    if request.method == "GET":
        return render_template("profile.html")
    if request.method == "POST":
        message = ""
        name = request.form.get("name")
        if name and name != current_user.name:  # type: ignore
            current_user.name = name
        else:
            pass
        old_pass = request.form.get("o_pass")
        new_pass = request.form.get("n_pass")
        if old_pass and new_pass:
            if old_pass == current_user.password:  # type: ignore
                current_user.password = new_pass
            else:
                message = "Old password does not match!"
        db.session.commit()
        return render_template("profile.html", message=message)


@app.route("/terms&conditions")
def terms_conditions():
    return render_template("terms&conditions.html")


@app.route("/admin_login", methods=["GET", "POST"])  # type: ignore
def admin_login():
    if request.method == "GET":
        return render_template("admin_login.html")
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        message = ""
        if username == "sidd" and password == "2003":
            return redirect(url_for("admin_dashboard"))
        else:
            message = "Invalid Credentials!!"
            return render_template("admin_login.html", message=message)


def gen_ratings_graph(ratings_list, count):
    plt.clf()
    bins = [1, 2, 3, 4, 5]
    plt.hist(
        ratings_list, bins=bins, color="#304674", edgecolor="white"
    )  # color='#72d3fe')
    plt.xlabel("Rating")
    plt.ylabel("Songs")
    plt.title("Song Ratings")
    ratings_filename = "ratings.png"
    plt.savefig(os.path.join("static", "graphs", ratings_filename))
    return ratings_filename


def gen_genre_graph(songs, count):
    plt.clf()
    genre_dict = {
        "Electronic_Dance": 0,
        "Rock": 0,
        "Jazz": 0,
        "Dubstep": 0,
        "Rhythm_and_Blues": 0,
        "Techno": 0,
        "Country_Music": 0,
        "Electro": 0,
        "Indie_Rock": 0,
        "Pop": 0,
    }
    for song in songs:
        genre_dict[song.genre] += 1
    pie_list = []
    pie_labels = []
    for genre in genre_dict:
        pie_list.append(genre_dict[genre])
        pie_labels.append(genre)
    plt.pie(pie_list, labels=pie_labels, autopct="%.2f%%")
    plt.title("Genres")
    genre_filename = "genre.png"
    plt.savefig(os.path.join("static", "graphs", genre_filename))
    print(genre_dict)
    print(pie_list)
    print(pie_labels)
    return genre_filename


@app.route("/admin_dashboard", methods=["GET", "POST"])  # type: ignore
def admin_dashboard():
    global count
    count += 1
    users = User.query.all()
    songs = Song.query.all()
    albums = Album.query.all()
    creator_count = 0
    for user in users:
        if user.user_type == "creator":
            creator_count += 1
    plays = 0
    ratings = []
    most_played = ""
    highest_plays = 0
    for song in songs:
        plays += song.played
        ratings.append(song.rating)
        if song.played > highest_plays:
            highest_plays = song.played
            most_played = song.song_name
    general_user_count = len(users) - creator_count
    ratings_graph_path = gen_ratings_graph(ratings, count)
    genre_graph_path = gen_genre_graph(songs, count)
    return render_template(
        "admin_dashboard.html",
        creator_count=creator_count,
        general_user_count=general_user_count,
        songs=songs,
        albums=albums,
        users_count=len(users),
        plays=plays,
        ratings_graph_path=ratings_graph_path,
        genre_graph_path=genre_graph_path,
        most_played=most_played,
        highest_plays=highest_plays,
    )


@app.route("/admin_songs", methods=["GET", "POST"])
def admin_songs():
    songs = Song.query.all()
    return render_template("admin_songs.html", songs=songs, Album=Album)


@app.route("/listen_admin_song/<int:song_id>")
def listen_admin_song(song_id):
    song = Song.query.filter_by(song_id=song_id).first()
    print("song is", song)
    return render_template("listen_admin_song.html", song=song)


@app.route("/delete_admin_song/<int:song_id>")
def delete_admin_song(song_id):
    song = Song.query.filter_by(song_id=song_id).first()
    db.session.delete(song)
    db.session.commit()
    return redirect(url_for("admin_songs"))


@app.route("/admin_albums")
def admin_albums():
    albums = Album.query.all()
    return render_template("admin_albums.html", albums=albums)


@app.route("/delete_admin_album/<int:album_id>")
def delete_admin_album(album_id):
    album = Album.query.filter_by(album_id=album_id).first()
    db.session.delete(album)
    db.session.commit()
    return redirect(url_for("admin_albums"))


@app.route("/all_creators", methods=["GET", "POST"])
def all_creators():
    creators = User.query.filter_by(user_type="creator").all()
    return render_template("all_creators.html", creators=creators)


@app.route("/blacklist/<int:user_id>")
def blacklist(user_id):
    creator = User.query.filter_by(user_id=user_id).first()
    creator.blacklisted = not creator.blacklisted
    db.session.commit()
    return redirect(url_for("all_creators"))


def admin_search_func(q):
    query = "%" + str(q) + "%"
    songs = Song.query.filter(Song.song_name.like(query)).all()
    artist_song = Song.query.filter(Song.artist.like(query)).all()
    artists = []
    artist_user = []
    for a in artist_song:
        if a.artist not in artists:
            artists.append(a.artist)
    for i in artists:
        user = User.query.filter_by(name=i, user_type="creator").first()
        artist_user.append(user)
    albums = Album.query.filter(Album.album_name.like(query)).all()
    return songs, artist_user, albums


@app.route("/admin_search", methods=["GET", "POST"])  # type: ignore
def admin_search():
    if request.method == "GET":
        return "Made a get request"
    if request.method == "POST":
        if "query" in request.form:
            query = request.form["query"]
            songs, artists, albums = admin_search_func(query)
            return render_template(
                "admin_search.html", songs=songs, artists=artists, albums=albums
            )


@app.route("/logout")
@login_required
def log_user_out():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
