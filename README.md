# Spotify Clone

## Introduction
This repository contains the backend codebase for the final project - Spotify Clone (FullStack).

## Description
The project is meant to clone the basic functionalities of the frontend for the [Spotify Website](https://open.spotify.com/). 

### APIs implemented using the Rest Framework
APIs for the website include:
1. Login
2. Signup
3. Update Profile (name and photo)
4. CRUD Albums (+ filters)
5. CRUD Songs (+ filters)
6. Increment song streams
7. CRUD Genre (for albums)
8. CRUD Playlists <sup>new</sup>
9. CRUD Tracks <sup>new</sup>
10. GET newly created playlists <sup>new</sup>
11. GET Queue for Player <sup>new</sup>
12. CRUD UserData <sup>new</sup>
    1. liked_albums
    2. liked_songs
    3. liked_playlists
    4. recently_played
    5. user_library
    6. followers
    7. following
13. GET Search <sup>new</sup>

## Clone the repository

Run the following commands to clone the repository and test out the song-album branch.

`$ git init`

`$ git clone https://gitlab.arbisoft.com/minahil.faisal/final-project-backend.git`

`$ cd final-project-backend`

`$ git pull origin playlist`

## Installation / Project Setup
This Django project uses pyenv, Django version 3.2 and python version 3.9.7

First, create a python environment to work in based on the python version.

`$ pyenv virtualenv 3.9.7 test-env`

Activate the environment

`$ pyenv activate test-env`

Install the requirements to run the project

`$ pip install -r requirements/requirements.txt`

Make migrations

`$ python manage.py migrate`

For testing out localhost:8000/admin, create a superuser.

`$ python manage.py createsuperuser`

**Note:** date-of-birth format for creating a superuser through the terminal is YYYY-MM-DD. Gender can be 'M' or 'F' for simplicity.

Now, load fixture data into the apps using this command:

` python manage.py loaddata fixtures/User.json --app users.User && python manage.py loaddata fixtures/Genre.json --app songs.Genre && python manage.py loaddata fixtures/Album.json --app songs.Album && python manage.py loaddata fixtures/Song.json --app songs.Song && python manage.py loaddata fixtures/Playlist.json --app playlists.Playlist && python manage.py loaddata fixtures/Track.json --app playlists.Track && python manage.py loaddata fixtures/UserData.json --app userdata.UserData && python manage.py loaddata fixtures/RecentlyPlayedAlbum.json --app userdata.RecentlyPlayedAlbum && python manage.py loaddata fixtures/RecentlyPlayedPlaylist.json --app userdata.RecentlyPlayedPlaylist && python manage.py loaddata fixtures/UserAlbumLibrary.json --app userdata.UserAlbumLibrary && python manage.py loaddata fixtures/UserArtistLibrary.json --app userdata.UserArtistLibrary && python manage.py loaddata fixtures/UserPlaylistLibrary.json --app userdata.UserPlaylistLibrary `

Now, run the server

`$ python manage.py runserver`

You can login using the following test credentials:

**username:** minahil (account with admin priviledges)

**password:** testing321

or you can create a new account (without admin priviledges) and search for "User" or Minahil Admin.

## Active Routes

All routes are updated and posted with updated on [Postman](https://red-star-992104.postman.co/workspace/Arbisoft---Training~9426c582-d5a1-41d3-bbdc-cef862074158/collection/29007347-e52fc81a-52ac-4b59-9833-17c560295696?action=share&creator=29007347). 

Login: http://localhost:8000/api/users/login/

Signup: http://localhost:8000/api/users/signup/

Update Profile: http://localhost:8000/api/users/update_profile/{username}/

**Note:** accessing http://localhost:8000/ will throw an error.

## New Routes

Genre: http://localhost:8000/api/genre/

Albums: http://localhost:8000/api/albums/

Songs: http://localhost:8000/api/songs/

Playlists: http://localhost:8000/api/playlists/

Tracks (for playlists): http://localhost:8000/api/tracks/

UserData: http://localhost:8000/api/userdata/ +

1. liked_albums/
2. liked_songs/
3. liked_playlists/
4. recently_played/ +
    1. <username>/update_albums/
    2. <username>/update_playlists/
5. user_library/
6. followers/
7. following/

**Note:** accessing just http://localhost:8000/api/userdata/ will throw an error.

Search: http://localhost:8000/api/userdata/search/<search_keyword>/

## Project status
Completed. Under Review.
