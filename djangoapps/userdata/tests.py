from django.test import override_settings
from rest_framework.test import APITestCase

from djangoapps.testing import make_user
from djangoapps.playlists.models import Playlist
from djangoapps.songs.models import Album, Genre, Song
from djangoapps.userdata.models import UserArtistLibrary, UserData


class UserDataTestCase(APITestCase):
    def setUp(self):
        self.alice = make_user('alice')
        self.eve = make_user('eve')
        self.artist = make_user('artist', is_artist=True)
        genre = Genre.objects.create(genre_name='Pop', color='#fff')
        self.album = Album.objects.create(
            artist=self.artist, album_name='A', album_publish_year=2020, genre=genre)
        self.song = Song.objects.create(album=self.album, song_name='Hit', track_number=1)

    def liked_song_ids(self, user):
        return set(UserData.objects.get(user=user).liked_songs.values_list('id', flat=True))


class LikeTests(UserDataTestCase):
    def test_can_like_and_unlike_own(self):
        self.client.force_authenticate(self.alice)
        url = '/api/userdata/liked_songs/alice/'
        self.assertEqual(self.client.put(url, {'liked_songs': self.song.id}, format='json').status_code, 200)
        self.assertEqual(self.liked_song_ids(self.alice), {self.song.id})
        self.client.put(url, {'liked_songs': self.song.id}, format='json')
        self.assertEqual(self.liked_song_ids(self.alice), set())

    def test_cannot_like_on_someone_elses_behalf(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/userdata/liked_songs/alice/', {'liked_songs': self.song.id}, format='json')
        self.assertEqual(res.status_code, 403)
        self.assertEqual(self.liked_song_ids(self.alice), set())

    def test_cannot_read_someone_elses_likes(self):
        self.client.force_authenticate(self.eve)
        self.assertEqual(self.client.get('/api/userdata/liked_songs/alice/').status_code, 403)

    def test_can_read_own_likes(self):
        self.client.force_authenticate(self.alice)
        self.assertEqual(self.client.get('/api/userdata/liked_songs/alice/').status_code, 200)

    def test_liking_missing_song_is_404_not_500(self):
        self.client.force_authenticate(self.alice)
        res = self.client.put('/api/userdata/liked_songs/alice/', {'liked_songs': 99999}, format='json')
        self.assertEqual(res.status_code, 404)

    def test_missing_body_field_is_400(self):
        self.client.force_authenticate(self.alice)
        self.assertEqual(self.client.put('/api/userdata/liked_songs/alice/', {}, format='json').status_code, 400)


class UserDataEndpointLockdownTests(UserDataTestCase):
    def test_cannot_list_everyones_data(self):
        self.client.force_authenticate(self.eve)
        self.assertEqual(self.client.get('/api/userdata/liked_songs/').status_code, 403)

    def test_cannot_delete_a_users_data(self):  # used to delete the whole UserData row
        self.client.force_authenticate(self.eve)
        self.assertEqual(self.client.delete('/api/userdata/liked_songs/alice/').status_code, 403)
        # not even your own: deleting UserData over the API is disabled
        self.client.force_authenticate(self.alice)
        self.assertEqual(self.client.delete('/api/userdata/liked_songs/alice/').status_code, 405)
        self.assertTrue(UserData.objects.filter(user=self.alice).exists())

    def test_cannot_update_someone_elses_recently_played(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/userdata/recently_played/alice/update_albums/',
                              {'recently_played_albums': self.album.id}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_can_update_own_recently_played(self):
        self.client.force_authenticate(self.alice)
        res = self.client.put('/api/userdata/recently_played/alice/update_albums/',
                              {'recently_played_albums': self.album.id}, format='json')
        self.assertEqual(res.status_code, 200)
        res = self.client.get('/api/userdata/recently_played/alice/')
        self.assertEqual(len(res.data['recents_list']), 1)

    def test_cannot_read_someone_elses_library(self):
        self.client.force_authenticate(self.eve)
        self.assertEqual(self.client.get('/api/userdata/user_library/alice/').status_code, 403)


class FollowTests(UserDataTestCase):
    def follow(self, who, target):
        self.client.force_authenticate(who)
        return self.client.put(f'/api/userdata/following/{who.username}/', {'following': target}, format='json')

    def test_follow_updates_both_sides_and_artist_library(self):
        self.assertEqual(self.follow(self.alice, 'artist').status_code, 200)
        self.assertTrue(UserData.objects.get(user=self.alice).following.filter(pk=self.artist.pk).exists())
        self.assertTrue(UserData.objects.get(user=self.artist).followers.filter(pk=self.alice.pk).exists())
        self.assertTrue(UserArtistLibrary.objects.filter(user=self.alice, artist=self.artist).exists())

        self.assertEqual(self.follow(self.alice, 'artist').data['status'], 'removed from following')
        self.assertFalse(UserData.objects.get(user=self.artist).followers.exists())
        self.assertFalse(UserArtistLibrary.objects.filter(user=self.alice).exists())

    def test_cannot_make_someone_else_follow(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/userdata/following/alice/', {'following': 'artist'}, format='json')
        self.assertEqual(res.status_code, 403)
        self.assertFalse(UserData.objects.get(user=self.alice).following.exists())

    def test_cannot_write_followers_directly(self):
        self.client.force_authenticate(self.eve)
        res = self.client.put('/api/userdata/followers/alice/', {'followers': 'eve'}, format='json')
        self.assertEqual(res.status_code, 403)
        self.client.force_authenticate(self.alice)
        res = self.client.put('/api/userdata/followers/alice/', {'followers': 'eve'}, format='json')
        self.assertEqual(res.status_code, 405)
        self.assertFalse(UserData.objects.get(user=self.alice).followers.exists())

    def test_cannot_follow_yourself(self):
        self.assertEqual(self.follow(self.alice, 'alice').status_code, 400)

    def test_follow_unknown_user_is_404(self):
        self.assertEqual(self.follow(self.alice, 'ghost').status_code, 404)

    def test_followers_and_following_are_public(self):
        self.follow(self.alice, 'artist')
        self.client.force_authenticate(self.eve)
        res = self.client.get('/api/userdata/followers/artist/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['followers'], [self.alice.id])
        self.assertEqual(self.client.get('/api/userdata/following/alice/').status_code, 200)


@override_settings(DEMO_READ_ONLY_USERS={'alice'})
class DemoUserDataTests(UserDataTestCase):
    def test_demo_account_can_still_like_and_follow(self):
        self.client.force_authenticate(self.alice)
        res = self.client.put('/api/userdata/liked_songs/alice/', {'liked_songs': self.song.id}, format='json')
        self.assertEqual(res.status_code, 200)
        res = self.client.put('/api/userdata/following/alice/', {'following': 'artist'}, format='json')
        self.assertEqual(res.status_code, 200)


class SearchTests(UserDataTestCase):
    def test_search_hides_private_playlists_and_limits_results(self):
        Playlist.objects.create(user=self.alice, playlist_name='hit list', description='')
        Playlist.objects.create(user=self.alice, playlist_name='hit secret', description='', is_private=True)
        for n in range(2, 9):
            Song.objects.create(album=self.album, song_name=f'Hit {n}', track_number=n)

        res = self.client.get('/api/userdata/search/hit/')
        self.assertEqual(res.status_code, 200)
        results = res.data['results']
        self.assertEqual([p['playlist_name'] for p in results['playlists']], ['hit list'])
        self.assertEqual(len(results['songs']), 5)
