#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from app import db

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', cascade='all,delete-orphan', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean(), nullable=False, default=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('Show', cascade='all,delete-orphan', backref='artist', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'), nullable=False)
    venue_name = db.Column(db.String, nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'), nullable=False)
    artist_name = db.Column(db.String, nullable=False)
    artist_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime, nullable=False)


# As an Artist or a Venue can have more than one Gender, it isn't the best practice to put a list as an attribute of a table
# because it can be very messy working with long strings separated by commas or any form to work a list as an attribute on
# databases, I found more simple to create a dictionary of Genders as a table and create Many to Many relationships between
# Artists-Genres and Venues-Genres as you can make the querys easier to implement with this model.

artists_genres = db.Table('artists_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

venues_genres = db.Table('venues_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Genre(db.Model):
	__tablename__ = 'genres'

	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(), nullable=False)
	artists = db.relationship('Artist', secondary=artists_genres,
		backref=db.backref('artist_genres', lazy=True))
	venues = db.relationship('Venue', secondary=venues_genres,
		backref=db.backref('venue_genres', lazy=True))
