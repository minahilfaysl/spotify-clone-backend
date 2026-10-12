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

`$ git clone https://github.com/minahilfaysl/spotify-clone-backend.git`

`$ cd spotify-clone-backend`

## Installation / Project Setup
This Django project uses Django 5.2 (LTS) and Python 3.12 or newer.

**No environment variables are needed for local development.** With nothing
set, the app runs in debug mode with a local SQLite database, the local
`media/` folder and a development-only secret key.

Create and activate a virtual environment:

`$ python3 -m venv .venv && source .venv/bin/activate`

Install the requirements to run the project

`$ pip install -r requirements.txt`

Apply migrations

`$ python manage.py migrate`

Load the demo data (users, albums, songs, playlists):

`$ python manage.py seed_demo`

For testing out localhost:8000/admin, create a superuser.

`$ python manage.py createsuperuser`

**Note:** date-of-birth format for creating a superuser through the terminal is YYYY-MM-DD. Gender can be 'M' or 'F' for simplicity.

Now, run the server

`$ python manage.py runserver`

You can login using the following test credentials:

**username:** minahil (account with admin privileges locally)
**password:** testing321

In production this demo account is read-only and has no admin access (see
[Demo accounts](#demo-accounts-are-read-only-in-production)).

or you can create a new account (without admin privileges) and search for "User" or Minahil Admin.

## Active Routes

Setup for testing and tracking on Postman.

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

## Deployment (Vercel + Neon + Cloudinary)

The API deploys to Vercel as a Django app. Uploaded media is stored on
Cloudinary and the database is Postgres (e.g. Neon).

Environment variables (Vercel → Project → Settings → Environment Variables):

| Variable | Value |
|---|---|
| `SECRET_KEY` | a long random string |
| `DATABASE_URL` | Postgres connection string (Neon: use the pooled one) |
| `CLOUDINARY_URL` | from the Cloudinary dashboard (`cloudinary://key:secret@cloud`) |
| `FRONTEND_URLS` | deployed frontend URL(s), comma-separated, no trailing slash |

No Neon or Cloudinary CLI, SDK setup or config files are needed; the app only
reads these variables.

On every deploy, `vercel_build.py` runs migrations, loads the demo fixtures
into an empty database, and uploads the demo media to Cloudinary if it isn't
there yet. It checks the Cloudinary credentials first and fails with a clear
message if they're wrong. Vercel limits request bodies to 4.5 MB, so uploads
(songs, photos) must be under that size.

To create your own admin account in production (the demo accounts can't use
`/admin/`), run once from this folder, with the production connection string:

`$ DATABASE_URL="<neon connection string>" python manage.py createsuperuser`

### Demo accounts are read-only in production

The seeded demo logins (e.g. `minahil` / `testing321`) are public, so in
production they can browse, play, like and follow, but cannot edit or delete
the demo albums, songs, playlists or profile, and get no Django admin access.
Visitors can sign up for their own account to try uploading and editing.
Set `DEMO_READ_ONLY_USERS` (comma-separated usernames, or empty to disable) to
change this. Locally (`DEBUG=True`) demo accounts are not restricted.

## Permissions

- Anyone can read public content: albums, songs, genres, public playlists,
  profiles, followers/following, search.
- Only the owner can change or delete their playlists (and tracks in them),
  albums and songs (artists only), and profile.
- Private playlists are only visible to their owner.
- Likes, library and recently played are private to their owner.
- Genres are managed by admins only.

## Running the tests

`$ python manage.py test djangoapps`

## Project status
Completed and deployed.
