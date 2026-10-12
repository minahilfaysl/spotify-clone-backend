from django.test import override_settings
from rest_framework.test import APITestCase

from djangoapps.testing import make_user
from djangoapps.songs.models import Album, Genre, Song


class SongsTestCase(APITestCase):
    def setUp(self):
        self.genre = Genre.objects.create(genre_name='Pop', color='#fff')
        self.artist = make_user('artist', is_artist=True)
        self.rival = make_user('rival', is_artist=True)
        self.listener = make_user('listener')
        self.album = Album.objects.create(
            artist=self.artist, album_name='First', album_publish_year=2020, genre=self.genre)
        self.song = Song.objects.create(album=self.album, song_name='Hit', track_number=1)


class AlbumTests(SongsTestCase):
    def test_album_is_created_for_the_logged_in_artist(self):
        self.client.force_authenticate(self.rival)
        res = self.client.post('/api/albums/', {
            'album_name': 'Mine', 'album_publish_year': 2024,
            'genre': self.genre.id, 'artist': self.artist.id,  # tries to impersonate
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Album.objects.get(album_name='Mine').artist, self.rival)

    def test_duplicate_album_name_is_400_not_500(self):
        self.client.force_authenticate(self.artist)
        res = self.client.post('/api/albums/', {
            'album_name': 'First', 'album_publish_year': 2024, 'genre': self.genre.id}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_listener_cannot_create_album(self):
        self.client.force_authenticate(self.listener)
        res = self.client.post('/api/albums/', {
            'album_name': 'Nope', 'album_publish_year': 2024, 'genre': self.genre.id}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_cannot_delete_another_artists_album(self):
        self.client.force_authenticate(self.rival)
        self.assertEqual(self.client.delete(f'/api/albums/{self.album.id}/').status_code, 403)
        self.assertTrue(Album.objects.filter(id=self.album.id).exists())

    def test_owner_can_delete_album(self):
        self.client.force_authenticate(self.artist)
        self.assertEqual(self.client.delete(f'/api/albums/{self.album.id}/').status_code, 204)

    def test_albums_are_public(self):
        self.assertEqual(self.client.get('/api/albums/').status_code, 200)


class SongTests(SongsTestCase):
    def test_song_detail_works(self):  # used to 500 (lookup_field='username')
        res = self.client.get(f'/api/songs/{self.song.id}/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['song_name'], 'Hit')

    def test_cannot_add_song_to_another_artists_album(self):
        self.client.force_authenticate(self.rival)
        res = self.client.post('/api/songs/', {
            'song_name': 'Sneaky', 'album': self.album.id, 'track_number': 2}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Song.objects.filter(song_name='Sneaky').exists())

    def test_cannot_edit_another_artists_song(self):
        self.client.force_authenticate(self.rival)
        res = self.client.patch(f'/api/songs/{self.song.id}/', {'song_name': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_top_tracks_for_unknown_artist_is_404(self):
        self.assertEqual(self.client.get('/api/songs/nobody/get_top_tracks/').status_code, 404)

    def test_top_tracks(self):
        res = self.client.get('/api/songs/artist/get_top_tracks/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data['results']), 1)


class StreamCountTests(SongsTestCase):
    def test_listener_can_count_a_play(self):
        self.client.force_authenticate(self.listener)
        res = self.client.post(f'/api/songs/{self.song.id}/increment_streams/')
        self.assertEqual(res.status_code, 200)
        self.song.refresh_from_db()
        self.assertEqual(self.song.total_streams, 1)

    def test_get_does_not_count_a_play(self):
        self.client.force_authenticate(self.listener)
        res = self.client.get(f'/api/songs/{self.song.id}/increment_streams/')
        self.assertEqual(res.status_code, 405)
        self.song.refresh_from_db()
        self.assertEqual(self.song.total_streams, 0)

    def test_anonymous_cannot_count_plays(self):
        res = self.client.post(f'/api/songs/{self.song.id}/increment_streams/')
        self.assertEqual(res.status_code, 401)


class GenreTests(SongsTestCase):
    def test_users_cannot_create_genres(self):
        self.client.force_authenticate(self.artist)
        res = self.client.post('/api/genre/', {'genre_name': 'Spam', 'color': '#000'}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_users_cannot_delete_genres(self):
        self.client.force_authenticate(self.artist)
        self.assertEqual(self.client.delete(f'/api/genre/{self.genre.id}/').status_code, 403)

    def test_genres_are_public(self):
        self.assertEqual(self.client.get('/api/genre/').status_code, 200)


@override_settings(DEMO_READ_ONLY_USERS={'artist'})
class DemoArtistTests(SongsTestCase):
    def test_demo_artist_cannot_delete_seeded_album(self):
        self.client.force_authenticate(self.artist)
        self.assertEqual(self.client.delete(f'/api/albums/{self.album.id}/').status_code, 403)
        self.assertTrue(Album.objects.filter(id=self.album.id).exists())

    def test_demo_artist_can_still_play_music(self):
        self.client.force_authenticate(self.artist)
        res = self.client.post(f'/api/songs/{self.song.id}/increment_streams/')
        self.assertEqual(res.status_code, 200)
