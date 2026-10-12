from django.test import override_settings
from rest_framework.test import APITestCase

from djangoapps.testing import make_user
from djangoapps.playlists.models import Playlist, Track
from djangoapps.songs.models import Album, Genre, Song


class PlaylistTestCase(APITestCase):
    def setUp(self):
        self.owner = make_user('owner')
        self.other = make_user('other')
        self.public = Playlist.objects.create(user=self.owner, playlist_name='Public', description='')
        self.private = Playlist.objects.create(
            user=self.owner, playlist_name='Secret', description='', is_private=True)
        genre = Genre.objects.create(genre_name='Pop', color='#fff')
        album = Album.objects.create(
            artist=make_user('artist', is_artist=True), album_name='A',
            album_publish_year=2020, genre=genre)
        self.song = Song.objects.create(album=album, song_name='Song', track_number=1)
        self.track = Track.objects.create(playlist=self.public, song=self.song)
        self.secret_track = Track.objects.create(playlist=self.private, song=self.song)

    def ids(self, res):
        return {item['id'] for item in res.data['results']}


class PlaylistOwnershipTests(PlaylistTestCase):
    def test_non_owner_cannot_delete(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f'/api/playlists/{self.public.id}/').status_code, 403)
        self.assertTrue(Playlist.objects.filter(id=self.public.id).exists())

    def test_non_owner_cannot_rename(self):
        self.client.force_authenticate(self.other)
        res = self.client.patch(f'/api/playlists/{self.public.id}/', {'playlist_name': 'Hacked'}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_owner_can_delete(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f'/api/playlists/{self.public.id}/').status_code, 204)

    def test_new_playlist_belongs_to_creator(self):
        self.client.force_authenticate(self.other)
        res = self.client.post('/api/playlists/', {
            'playlist_name': 'Mine', 'description': 'mine', 'user': self.owner.id}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Playlist.objects.get(playlist_name='Mine').user, self.other)


class PlaylistPrivacyTests(PlaylistTestCase):
    def test_private_playlists_hidden_from_other_users(self):
        self.client.force_authenticate(self.other)
        ids = self.ids(self.client.get('/api/playlists/'))
        self.assertIn(self.public.id, ids)
        self.assertNotIn(self.private.id, ids)

    def test_private_playlists_hidden_from_visitors(self):
        self.assertNotIn(self.private.id, self.ids(self.client.get('/api/playlists/')))

    def test_private_playlists_hidden_when_filtering_by_owner(self):
        self.client.force_authenticate(self.other)
        ids = self.ids(self.client.get('/api/playlists/?user__username=owner'))
        self.assertEqual(ids, {self.public.id})

    def test_private_playlist_detail_is_404_for_others(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.get(f'/api/playlists/{self.private.id}/').status_code, 404)

    def test_owner_sees_own_private_playlists(self):
        self.client.force_authenticate(self.owner)
        ids = self.ids(self.client.get('/api/playlists/?user__username=owner'))
        self.assertEqual(ids, {self.public.id, self.private.id})

    def test_private_tracks_hidden_from_others(self):
        self.client.force_authenticate(self.other)
        res = self.client.get(f'/api/tracks/?playlist={self.private.id}')
        self.assertEqual(self.ids(res), set())


class TrackOwnershipTests(PlaylistTestCase):
    def test_cannot_add_track_to_someone_elses_playlist(self):
        self.client.force_authenticate(self.other)
        res = self.client.post('/api/tracks/', {'playlist': self.public.id, 'song': self.song.id}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_cannot_remove_track_from_someone_elses_playlist(self):
        self.client.force_authenticate(self.other)
        self.assertEqual(self.client.delete(f'/api/tracks/{self.track.id}/').status_code, 403)
        self.assertTrue(Track.objects.filter(id=self.track.id).exists())

    def test_owner_can_add_and_remove_tracks(self):
        self.client.force_authenticate(self.owner)
        res = self.client.post('/api/tracks/', {'playlist': self.public.id, 'song': self.song.id}, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(self.client.delete(f'/api/tracks/{res.data["id"]}/').status_code, 204)


@override_settings(DEMO_READ_ONLY_USERS={'owner'})
class DemoPlaylistTests(PlaylistTestCase):
    def test_demo_account_cannot_delete_its_seeded_playlists(self):
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.delete(f'/api/playlists/{self.public.id}/').status_code, 403)
