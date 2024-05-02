from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


liked_songs = db.Table(
    "liked_songs",
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), primary_key=True),
    db.Column("song_id", db.Integer, db.ForeignKey("song.song_id"), primary_key=True),
)
song_playlist = db.Table(
    "song_playlist",
    db.Column("song_id", db.Integer, db.ForeignKey("song.song_id"), primary_key=True),
    db.Column(
        "playlist_id",
        db.Integer,
        db.ForeignKey("playlist.playlist_id"),
        primary_key=True,
    ),
)  # many-many btwn song and playlist

song_rating = db.Table(
    "song_rating",
    db.Column("song_id", db.Integer, db.ForeignKey("song.song_id"), primary_key=True),
    db.Column("user_id", db.Integer, db.ForeignKey("user.user_id"), primary_key=True),
)


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(100), default="general_user")
    profile_pic = db.Column(db.String(100), nullable=False)
    blacklisted = db.Column(db.Boolean, default=False)
    songs = db.relationship(
        "Song", backref="singer"
    )  # many-one btwn song and user(creator)
    albums = db.relationship(
        "Album", backref="album_creator"
    )  # many-one btwn album and user(creator)
    playlists = db.relationship(
        "Playlist", backref="user_playlist"
    )  # many-one btwn playlist and user(general)
    liked_songs = db.relationship("Song", backref="fav_songs", secondary=liked_songs)
    rated_songs = db.relationship("Song", backref="rated_songs", secondary=song_rating)

    def get_id(self):
        return str(self.user_id)


class Song(db.Model):
    song_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    song_name = db.Column(db.String(100), nullable=False)
    lyrics = db.Column(db.String(1000), nullable=False)
    artist = db.Column(db.String(100), nullable=False)
    path = db.Column(db.String(100), nullable=False)
    poster = db.Column(db.String(100), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    rating = db.Column(db.Integer, default=0)
    genre = db.Column(db.String(100), nullable=False)
    played = db.Column(db.Integer, nullable=False, default=0)
    album = db.Column(db.Integer, db.ForeignKey("album.album_id"))
    creator = db.Column(
        db.Integer, db.ForeignKey("user.user_id")
    )  # one-many btwn user(creator) and song
    playlist = db.relationship("Playlist", backref="playlist", secondary=song_playlist)


class Album(db.Model):
    album_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    album_name = db.Column(db.String(100), nullable=False)
    poster = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False, default=0)
    artist = db.Column(db.Integer, nullable=False)
    creator = db.Column(
        db.Integer, db.ForeignKey("user.user_id")
    )  # one-many btwn user(creator) and album
    songs = db.relationship("Song", backref="song_album")


class Playlist(db.Model):
    playlist_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    user = db.Column(
        db.Integer, db.ForeignKey("user.user_id")
    )  # one-many btwn user(general) and playlist
