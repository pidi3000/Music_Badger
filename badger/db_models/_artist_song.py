from badger.extension import db


_artist_song = db.Table(
    'artist_song',
    db.Column('user_data_id', db.Integer, db.ForeignKey('song_user_data.id')),
    db.Column('artist_id', db.Integer, db.ForeignKey('artist.id'))
)
