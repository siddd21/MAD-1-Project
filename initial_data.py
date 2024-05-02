from models import *
from app import app

with app.app_context():
    db.drop_all()
    db.create_all()
    for i in range(1, 8):
        user = User(
            name=f"Creator-{i}",
            username=f"creator-{i}",
            password=f"creator-{i}",
            user_type="creator",
            profile_pic=f"creator-{i}.jpg",
        )
        db.session.add(user)
        db.session.commit()
    for i in range(1, 5):
        user = User(
            name=f"User-{i}",
            username=f"user-{i}",
            password=f"user-{i}",
            user_type="user",
            profile_pic=f"user-{i}.jpg",
        )
        db.session.add(user)
        db.session.commit()
    lyrics = """Lorem ipsum dolor sit amet consectetur, adipisicing elit. Fugiat dolorem dicta
    saepe quaerat facilis iure officiis nihil adipisci! Maxime ab enim eligendi
    rerum reiciendis animi unde recusandae ut deleniti assumenda. Lorem ipsum dolor
    sit amet consectetur adipisicing elit. Illum tenetur ab iste voluptatum totam
    inventore ex. Fuga mollitia aspernatur velit esse iste, alias aperiam neque
    libero, fugiat voluptatem, dolores minus. Lorem ipsum dolor sit amet
    consectetur, adipisicing elit. Fugiat dolorem dicta saepe quaerat facilis iure
    officiis nihil adipisci! Maxime ab enim eligendi rerum reiciendis animi unde
    recusandae ut deleniti assumenda. Lorem ipsum dolor sit amet consectetur
    adipisicing elit. Illum tenetur ab iste voluptatum totam inventore ex. Fuga
    mollitia aspernatur velit esse iste, alias aperiam neque libero, fugiat
    voluptatem, dolores minus. Lorem ipsum dolor sit amet consectetur, adipisicing
    elit. Fugiat dolorem dicta saepe quaerat facilis iure officiis nihil adipisci!
    Maxime ab enim eligendi rerum reiciendis animi unde recusandae ut deleniti
    assumenda. Lorem ipsum dolor sit amet consectetur adipisicing elit. Illum
    tenetur ab iste voluptatum totam inventore ex. Fuga mollitia aspernatur velit
    esse iste, alias aperiam neque libero, fugiat voluptatem, dolores minus. Lorem
    ipsum dolor sit amet consectetur, adipisicing elit. Fugiat dolorem dicta saepe
    quaerat facilis iure officiis nihil adipisci! Maxime ab enim eligendi rerum
    reiciendis animi unde recusandae ut deleniti assumenda. Lorem ipsum dolor sit
    amet consectetur adipisicing elit. Illum tenetur ab iste voluptatum totam
    inventore ex. Fuga mollitia aspernatur velit esse iste, alias aperiam neque
    libero, fugiat voluptatem, dolores minus."""
    genres = [
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
    for i in range(1, 31):
        x = i % 8
        g = i % 9
        song = Song(
            song_name=f"Song-{i}",
            artist=User.query.filter_by(user_id=x).first().name,
            path="audio-1.wav",
            poster=f"song-{i}.jpg",
            genre=genres[g],
            creator=x,
        )
        db.session.add(song)
        db.session.commit()

    for i in range(1, 6):
        g = i % 5
        album = Album(
            album_name=f"Album-{i}",
            poster=f"album-{i}.jpg",
            genre=genres[g],
            artist=User.query.filter_by(user_id=i).first().name,
            creator=i,
        )
        db.session.add(album)
        db.session.commit()

    for album in Album.query.all():
        creator = User.query.filter_by(user_id=Album.creator).first()
        creator_songs = creator.songs()
        if len(creator_songs) >= 3:
            for j in range((len(creator_songs) - 2)):
                album.songs.append(creator_songs[j])
            db.session.commit()
