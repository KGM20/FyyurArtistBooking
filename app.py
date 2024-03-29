#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
from datetime import datetime
from flask import Flask, render_template, abort, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from models import *

# TODO: connect to a local postgresql database - DONE

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/') 
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():

  data = []
  venues = db.session.query(Venue).all()

  for venue in venues:

    index = 'Not exist'
    for place in data:
      if venue.city == place['city'] and venue.state == place['state']:
        index = data.index(place)

    upcoming_shows = db.session.query(Show).filter_by(venue_id=venue.id).all()
    today = datetime.now()

    for show in upcoming_shows:
      if today > show.start_time:
        upcoming_shows.remove(show)

    if index == 'Not exist':
      data.append({
        'city': venue.city,
        'state': venue.state,
        'venues': [{
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': len(upcoming_shows),
        }]
      })
    else:
      data[index]['venues'].append({
        'id': venue.id,
        'name': venue.name,
        'num_upcoming_shows': len(upcoming_shows),
      })

  return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])  
def search_venues():
  response = {}
  name = request.form['search_term']
  
  data = db.session.query(Venue).filter(Venue.name.ilike('%'+name+'%')).all()
  count = len(data)

  response['count'] = count
  response['data'] = data

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')   
def show_venue(venue_id):

  data = {}
  venue = db.session.query(Venue).get(venue_id)

  # To show an error layout if venue_id index does not exist, instead of showing a server error
  try:
    genres = db.session.query(Genre).join(Genre.venues).filter_by(id=venue.id).all()
  except:
    abort (404)
  
  # Selecting genders
  venue_genres = []
  for genre in genres:
    venue_genres.append(genre.name)

  # Selecting shows
  shows = db.session.query(Show).filter_by(venue_id=venue.id).all()
  today = datetime.now()

  past_shows = []
  upcoming_shows = []

  for show in shows:

    artist = db.session.query(Artist).get(show.artist_id)
    show_data = {
        'artist_id': artist.id,
        'artist_name': artist.name,
        'artist_image_link': artist.image_link,
        'start_time': show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      }
    if today > show.start_time:  
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue_genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue.seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])  
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])  
def create_venue_submission():

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_description = request.form['seeking_description']

    if request.form['seeking_talent'] == 'Yes':
      seeking_talent = True
    else:
      seeking_talent = False

    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, 
      website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

    venue_genres = []

    for genre in genres:
      temp = db.session.query(Genre).filter_by(name=genre).first()
      if not temp:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        temp = new_genre

      venue_genres.append(temp)

    venue.venue_genres = venue_genres

    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('There was an error. ' + name + ' wasn\'t listed...')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])  
def delete_venue(venue_id):

  try:
    venue = db.session.query(Venue).get(venue_id) 
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')  
def artists():
  return render_template('pages/artists.html', artists=db.session.query(Artist).all())

@app.route('/artists/search', methods=['POST'])  
def search_artists():

  response = {}
  name = request.form['search_term']
  
  data = db.session.query(Artist).filter(Artist.name.ilike('%'+name+'%')).all()
  count = len(data)

  response['count'] = count
  response['data'] = data

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')  
def show_artist(artist_id):

  data = {}
  artist = db.session.query(Artist).get(artist_id)

  # To show an error layout if artist_id index not exists, instead of showing a server error
  try:
    genres = db.session.query(Genre).join(Genre.artists).filter_by(id=artist.id).all()
  except:
    abort (404)
  
  # Selecting genders
  artist_genres = []
  for genre in genres:
    artist_genres.append(genre.name)

  # Selecting shows
  shows = db.session.query(Show).filter_by(artist_id=artist.id).all()
  today = datetime.now()

  past_shows = []
  upcoming_shows = []

  for show in shows:

    venue = db.session.query(Venue).get(show.venue_id)
    show_data = {
        'venue_id': venue.id,
        'venue_name': venue.name,
        'venue_image_link': venue.image_link,
        'start_time': show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      }
    if today > show.start_time:  
      past_shows.append(show_data)
    else:
      upcoming_shows.append(show_data)

  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist_genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist.seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link
  data['past_shows'] = past_shows
  data['upcoming_shows'] = upcoming_shows
  data['past_shows_count'] = len(past_shows)
  data['upcoming_shows_count'] = len(upcoming_shows)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])   #NICE
def edit_artist(artist_id):
  form = ArtistForm()

  data = {}
  artist = db.session.query(Artist).get(artist_id)

  # To show an error layout if artist_id index not exists, instead of showing a server error
  try:
    genres = db.session.query(Genre).join(Genre.artists).filter_by(id=artist.id).all()
  except:
    abort (404)
  
  # Selecting genders with spaces to split() them on JS
  artist_genres = ''
  for genre in genres:
    artist_genres = artist_genres + genre.name + ' '

  if artist.seeking_venue:
    artist_seeking_venue = 'Yes'
  else:
    artist_seeking_venue = 'No'

  data['id'] = artist.id
  data['name'] = artist.name
  data['genres'] = artist_genres
  data['city'] = artist.city
  data['state'] = artist.state
  data['phone'] = artist.phone
  data['website'] = artist.website
  data['facebook_link'] = artist.facebook_link
  data['seeking_venue'] = artist_seeking_venue
  data['seeking_description'] = artist.seeking_description
  data['image_link'] = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False

  try:
    artist = db.session.query(Artist).get(artist_id)

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_description = request.form['seeking_description']

    if request.form['seeking_venue'] == 'Yes':
      seeking_venue = True
    else:
      seeking_venue = False

    artist_genres = []

    for genre in genres:
      temp = db.session.query(Genre).filter_by(name=genre).first()
      if not temp:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        temp = new_genre

      artist_genres.append(temp)

    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    artist.website = website
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.artist_genres = artist_genres

    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('There was an error. ' + name + ' wasn\'t updated...')
    error = True
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = {}
  venue = db.session.query(Venue).get(venue_id)

  # To show an error layout if venue_id index does not exist, instead of showing a server error
  try:
    genres = db.session.query(Genre).join(Genre.venues).filter_by(id=venue.id).all()
  except:
    abort (404)
  
  # Selecting genders with spaces to split() them on JS
  venue_genres = ''
  for genre in genres:
    venue_genres = venue_genres + genre.name + ' '

  if venue.seeking_talent:
    venue_seeking_talent = 'Yes'
  else:
    venue_seeking_talent = 'No'

  data['id'] = venue.id
  data['name'] = venue.name
  data['genres'] = venue_genres
  data['address'] = venue.address
  data['city'] = venue.city
  data['state'] = venue.state
  data['phone'] = venue.phone
  data['website'] = venue.website
  data['facebook_link'] = venue.facebook_link
  data['seeking_talent'] = venue_seeking_talent
  data['seeking_description'] = venue.seeking_description
  data['image_link'] = venue.image_link

  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  error = False
  try:

    venue = db.session.query(Venue).get(venue_id)

    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_description = request.form['seeking_description']

    if request.form['seeking_talent'] == 'Yes':
      seeking_talent = True
    else:
      seeking_talent = False

    venue_genres = []

    for genre in genres:
      temp = db.session.query(Genre).filter_by(name=genre).first()
      if not temp:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        temp = new_genre

      venue_genres.append(temp)

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.image_link = image_link
    venue.facebook_link = facebook_link
    venue.website = website
    venue.seeking_description = seeking_description
    venue.seeking_talent = seeking_talent
    venue.venue_genres = venue_genres

    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('There was an error. ' + name + ' wasn\'t updated...')
    error = True
  finally:
    db.session.close()
  if error:
    return render_template('pages/home.html')
  else:
   return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])  
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])  
def create_artist_submission():

  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    image_link = request.form['image_link']
    genres = request.form.getlist('genres')
    facebook_link = request.form['facebook_link']
    website = request.form['website']
    seeking_description = request.form['seeking_description']

    if request.form['seeking_venue'] == 'Yes':
      seeking_venue = True
    else:
      seeking_venue = False

    artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link, 
      website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)

    artist_genres = []

    for genre in genres:
      temp = db.session.query(Genre).filter_by(name=genre).first()
      if not temp:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        temp = new_genre

      artist_genres.append(temp)

    artist.artist_genres = artist_genres

    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + name + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('There was an error. ' + name + ' wasn\'t listed...')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows') 
def shows():

  data = []
  shows = db.session.query(Show).all()

  for show in shows:
    artist = db.session.query(Artist).get(show.artist_id)
    venue = db.session.query(Venue).get(show.venue_id)
    temp = {
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "artist_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    data.append(temp)

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    # I know I should have validated the start_time better because it's really easy to get an error with that
    # but I tried using the WTForm validators and I couldn't get them to work, not even the custom ones with
    # the examples on their documentation, making new ones or the Regexp one because I even had the regexp  
    # ready and tested on a local program
    start_time = datetime.strptime(request.form['start_time'], "%Y-%m-%d %H:%M")

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)

    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
