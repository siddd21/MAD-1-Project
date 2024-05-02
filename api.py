from flask import Flask, request, abort, jsonify
from flask_restful import Api, Resource, reqparse  # type: ignore
from models import *
from app import app

api = Api(app)

parser = reqparse.RequestParser()

parser.add_argument("song_name", type=str)
parser.add_argument("song_creator", type=int)
parser.add_argument("song_lyrics", type=str)
parser.add_argument("song_genre", type=str)
parser.add_argument("song_path", type=str)

parser.add_argument("playlist_name", type=str)
parser.add_argument("playlist_user", type=int)
parser.add_argument("playlist_songs", type=list, location="json")
parser.add_argument("playlist_add_songs", type=list, location="json")
parser.add_argument("playlist_delete_songs", type=list, location="json")

parser.add_argument("album_name", type=str)
parser.add_argument("album_poster", type=str)
parser.add_argument("album_genre", type=str)
parser.add_argument("album_creator", type=int)
parser.add_argument("album_songs", type=list, location="json")
parser.add_argument("album_add_songs", type=list, location="json")
parser.add_argument("album_delete_songs", type=list, location="json")


class SongApi(Resource):
    def get(self):
        songs = Song.query.all()
        i = 1
        all_songs = {}
        for song in songs:
            this_song = {}
            this_song["song_id"] = song.song_id
            this_song["song_name"] = song.song_name
            this_song["song_artist"] = song.artist
            this_song["song_genre"] = song.genre
            this_song["song_rating"] = song.rating
            this_song["song_lyrics"] = song.lyrics
            all_songs[f"song_{i}"] = this_song
            i += 1
        return all_songs

    def post(self):
        args = parser.parse_args()
        creator = args["song_creator"]
        genre = args["song_genre"]
        lyrics = args["song_lyrics"]
        name = args["song_name"]
        path = args["song_path"]
        genre_list = [
            "Electronic_Dance",
            "Rock",
            "Jazz",
            "Dubstep",
            "Rhythm_and_Blues",
            "Techno",
            "Country_Music",
            "Electro",
            "Indie_Rock",
            "Pop",
        ]
        creators = User.query.filter_by(user_type="creator").all()
        creator_ids = []
        for c in creators:
            creator_ids.append(c.user_id)
        if creator and genre and lyrics and name and path:
            if (
                creator != ""
                and genre != ""
                and lyrics != ""
                and name != ""
                and path != ""
            ):
                if creator in creator_ids and genre in genre_list:
                    artist = User.query.filter_by(user_id=creator).first()
                    poster = "default poster.jpg"
                    new_song = Song(
                        song_name=args["song_name"],
                        lyrics=args["song_lyrics"],
                        artist=artist.name,
                        poster=poster,
                        genre=genre,
                        creator=creator,
                        path=args["song_path"],
                    )
                    db.session.add(new_song)
                    db.session.commit()
                    return {"message": f"{new_song} added successfully"}, 201
                elif creator not in creator_ids:
                    return {"message": "Creator does not exist"}, 400
                elif genre not in genre_list:
                    return {
                        "message": f"Select a valid genre from this the list {genre_list}"
                    }, 400
            else:
                return {"message": "Inavlid Parameters!"}, 400
        else:
            return {"message": "Inavlid Parameters!"}, 400

    def put(self, s_id):
        args = parser.parse_args()
        song = Song.query.filter_by(song_id=s_id).first()
        genre_list = [
            "Electronic_Dance",
            "Rock",
            "Jazz",
            "Dubstep",
            "Rhythm_and_Blues",
            "Techno",
            "Country_Music",
            "Electro",
            "Indie_Rock",
            "Pop",
        ]
        name = args["song_name"]
        genre = args["song_genre"]
        lyrics = args["song_lyrics"]
        if name or genre or lyrics:
            if name is not None:
                if name != "":
                    song.song_name = name
                else:
                    return {"message": "Provide a valid name"}
            if genre is not None:
                if genre in genre_list:
                    song.genre = genre
                else:
                    return {
                        "message": f"Select a valid genre from this the list {genre_list}"
                    }, 400
            if lyrics is not None:
                if lyrics != "":
                    song.lyrics = lyrics
                else:
                    return {"message": "Provide a valid lyrics"}
            db.session.commit()
            return {"message": f"{song} updated successfully"}, 200
        else:
            return {"message": "Bad request"}, 400

    def delete(self, s_id):
        song = Song.query.filter_by(song_id=s_id).first()
        if song is not None:
            db.session.delete(song)
            db.session.commit()
            return ({"message": "Deleted Successfully"}, 204)
        else:
            return {"message": "Song does not exist"}, 400


api.add_resource(
    SongApi,
    "/api/all_songs",
    "/api/add_song",
    "/api/update_song/<int:s_id>",
    "/api/delete_song/<int:s_id>",
)


class PlaylistApi(Resource):
    def get(self):
        playlists = Playlist.query.all()
        i = 1
        all_playlists = {}
        for play_list in playlists:
            this_playlist = {}
            this_playlist["playlist_id"] = play_list.playlist_id
            this_playlist["playlist_name"] = play_list.name
            this_playlist["playlist_user"] = (
                User.query.filter_by(user_id=play_list.user).first().name
            )
            playlist_songs = play_list.playlist
            songs = []
            for song in playlist_songs:
                songs.append(song.song_name)
            this_playlist["playlist_songs"] = songs
            all_playlists[f"playlist_{i}"] = this_playlist
            i += 1
        return all_playlists

    def delete(self, p_id):
        playlist = Playlist.query.filter_by(playlist_id=p_id).first()
        if playlist is not None:
            db.session.delete(playlist)
            db.session.commit()
            return {"message": "Playlist deleted successfully"}, 204
        else:
            return {"message": "Playlist does not exist"}, 400

    def post(self):
        args = parser.parse_args()
        playlist_name = args["playlist_name"]
        user_id = args["playlist_user"]
        song_ids = args["playlist_songs"]
        print(song_ids)
        if user_id is not None:
            playlist_user = User.query.filter_by(user_id=user_id).first()
        else:
            playlist_user = None
        flag = True
        songs = []
        for song_id in song_ids:
            song = Song.query.filter_by(song_id=int(song_id)).first()
            if song is not None:
                songs.append(song)
            else:
                flag = False
                break
        print(songs)
        if playlist_name is not None and playlist_name != "":
            if playlist_user is not None:
                if flag == True:
                    to_add = Playlist(name=playlist_name, user=int(user_id))
                    db.session.add(to_add)
                    db.session.commit()
                    for song in songs:
                        to_add.playlist.append(song)
                    db.session.commit()
                else:
                    return {"message": "Song(s) does not exist!"}, 400
            else:
                return {"message": "User not found!"}, 400
        else:
            return {"message": "Provide a valid name!"}, 400
        return {"message": "Playlist created successfully!"}, 201

    def put(self, p_id):
        args = parser.parse_args()
        playlist_name = args["playlist_name"]
        user_id = args["playlist_user"]
        add_song_ids = args["playlist_add_songs"]
        delete_song_ids = args["playlist_delete_songs"]
        play_list = Playlist.query.filter_by(playlist_id=p_id).first()

        if user_id is not None and user_id != "":
            if play_list.user != int(user_id):
                return {"message": "Playlist does not belong to the given user!"}, 400
        else:
            return {"message": "User not found!"}, 400
        flag_a = True
        flag_d = True
        add_songs = []

        if delete_song_ids is not None:
            for song_id in delete_song_ids:
                song = Song.query.filter_by(song_id=int(song_id)).first()
                if song in play_list.playlist:
                    play_list.playlist.remove(song)
                else:
                    flag_d = False
                    break

        if flag_d == False:
            return {"message": "Song(s) not found in playlist"}, 400

        if add_song_ids is not None:
            for song_id in add_song_ids:
                song = Song.query.filter_by(song_id=int(song_id)).first()
                if song is not None:
                    add_songs.append(song)
                else:
                    flag_a = False
                    break

        if playlist_name is not None:
            if playlist_name != "":
                play_list.name = playlist_name
                db.session.commit()
            else:
                return {"message": "Provide a valid name!"}, 400

        if flag_a:
            for song in add_songs:
                if song not in play_list.playlist:
                    play_list.playlist.append(song)
            db.session.commit()
        else:
            return {"message": "Song(s) does not exist!"}, 400

        db.session.commit()
        return {"message": "Playlist updated successfully"}, 200


api.add_resource(
    PlaylistApi,
    "/api/all_playlist",
    "/api/delete_playlist/<int:p_id>",
    "/api/add_playlist",
    "/api/update_playlist/<int:p_id>",
)


class UserApi(Resource):
    def get(self):
        users = User.query.all()
        all_users = {}
        i = 1
        for user in users:
            this_user = {}
            this_user["user_id"] = user.user_id
            this_user["name"] = user.name
            this_user["username"] = user.username
            this_user["user_type"] = user.user_type
            if user.user_type == "creator":
                songs = Song.query.filter_by(creator=user.user_id)
                song_name = []
                for song in songs:
                    song_name.append(song.song_name)
                this_user["songs"] = song_name
            all_users[f"user_{i}"] = this_user
            i += 1
        return all_users, 200


api.add_resource(UserApi, "/api/all_users")


class AlbumApi(Resource):
    def get(self):
        albums = Album.query.all()
        i = 1
        all_albums = {}
        for album in albums:
            this_album = {}
            this_album["album_id"] = album.album_id
            this_album["album_name"] = album.album_name
            this_album["album_genre"] = album.genre
            this_album["album_artist"] = album.artist
            this_album["album_rating"] = album.rating
            album_songs = album.songs
            songs = []
            for song in album_songs:
                songs.append(song.song_name)
            this_album["album_songs"] = songs
            all_albums[f"album_{i}"] = this_album
            i += 1
        return all_albums, 200

    def delete(self, a_id, u_id):
        album = Album.query.filter_by(album_id=a_id).first()
        if album is not None:
            if album.creator == u_id:
                db.session.delete(album)
                db.session.commit()
                return {"message": "Album deleted successfully"}, 204
            else:
                return {"message": "Album does not belong to the given creator"}, 400
        else:
            return {"message": "Album does not exist!"}, 400

    def post(self):
        args = parser.parse_args()
        name = args["album_name"]
        poster = args["album_poster"]
        genre = args["album_genre"]
        creator = args["album_creator"]
        song_ids = args["album_songs"]
        genre_list = [
            "Electronic_Dance",
            "Rock",
            "Jazz",
            "Dubstep",
            "Rhythm_and_Blues",
            "Techno",
            "Country_Music",
            "Electro",
            "Indie_Rock",
            "Pop",
        ]
        if creator is not None and creator != "":
            artist = User.query.filter_by(user_id=creator).first()
            if artist.user_type != "creator":
                return {"message": "Only creator can create albums!"}, 400
        else:
            return {"message": "Invalid creator!"}, 400

        flag = True
        songs = []
        for song_id in song_ids:
            song = Song.query.filter_by(song_id=song_id).first()
            if song is not None:
                songs.append(song)
                if song.creator != creator:
                    flag = False
                    break
                if song.album is not None:
                    flag = False
                    break
            else:
                flag = False
                break
        if name is not None and name != "":
            if poster is not None and poster != "":
                if genre is not None and genre in genre_list:
                    if flag:
                        to_add = Album(
                            album_name=name,
                            poster=poster,
                            genre=genre,
                            artist=artist.name,
                            creator=creator,
                        )
                        db.session.add(to_add)
                        db.session.commit()
                        print(to_add)
                        for song in songs:
                            to_add.songs.append(song)
                        db.session.commit()
                    else:
                        return {"message": "Invalid songs"}, 400
                else:
                    return {
                        "message": f"Select a valid genre from this the list {genre_list}"
                    }, 400
            else:
                return {"message": "Invalid poster"}, 400
        else:
            return {"message": "Invalid name"}, 400
        return {"message": "Album created successfully"}, 201

    def put(self, a_id, c_id):
        args = parser.parse_args()
        name = args["album_name"]
        poster = args["album_poster"]
        genre = args["album_genre"]
        add_song_ids = args["album_add_songs"]
        delete_song_ids = args["album_delete_songs"]
        album = Album.query.filter_by(album_id=a_id).first()
        creator = User.query.filter_by(user_id=c_id).first()
        genre_list = [
            "Electronic_Dance",
            "Rock",
            "Jazz",
            "Dubstep",
            "Rhythm_and_Blues",
            "Techno",
            "Country_Music",
            "Electro",
            "Indie_Rock",
            "Pop",
        ]

        if album.creator != creator.user_id:
            return {"message": "Album does not belong to the given artist"}, 400

        flag_a = True
        flag_d = True
        add_songs = []

        if add_song_ids is not None:
            for song_id in add_song_ids:
                song = Song.query.filter_by(song_id=song_id).first()
                if song is not None:
                    if song.creator == c_id:
                        if song.album is None:
                            add_songs.append(song)
                        else:
                            flag_a = False
                            break
                    else:
                        flag_a = False
                        break
                else:
                    flag_a = False
                    break

        if delete_song_ids is not None:
            for song_id in delete_song_ids:
                song = Song.query.filter_by(song_id=song_id).first()
                if song is not None:
                    if song in album.songs:
                        album.songs.remove(song)
                    else:
                        flag_d = False
                        break
                else:
                    flag_d = False
                    break

        if name is not None and name != "":
            if genre is not None and genre in genre_list:
                if poster is not None and poster != "":
                    if flag_a:
                        if flag_d:
                            album.album_name = name
                            album.genre = genre
                            album.poster = poster
                            for song in add_songs:
                                album.songs.append(song)
                            db.session.commit()
                        else:
                            return {"message": "Invalid songs to delete"}, 400
                    else:
                        return {"message": "Invalid songs to add"}, 400
                else:
                    return {"message": "Invalid poster"}, 400
            else:
                return {"message": "Invalid genre"}, 400
        else:
            return {"message": "Invalid name"}, 400

        db.session.commit()
        return {"message": "Album updated successfully"}, 201


api.add_resource(
    AlbumApi,
    "/api/all_albums",
    "/api/delete_album/<int:a_id>/<int:u_id>",
    "/api/add_album",
    "/api/update_album/<int:a_id>/<int:c_id>",
)

app.run(debug=True)
