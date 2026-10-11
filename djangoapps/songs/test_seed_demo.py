from io import StringIO
from unittest import mock

import cloudinary.exceptions
from django.core.management import CommandError, call_command
from django.test import TestCase, override_settings

from djangoapps.testing import User

CLOUDINARY = 'cloudinary://key:secret@demo-cloud'


def run_seed(**kwargs):
    out = StringIO()
    call_command('seed_demo', stdout=out, **kwargs)
    return out.getvalue()


class SeedWithoutCloudinaryTests(TestCase):
    @override_settings(CLOUDINARY_URL=None)
    def test_loads_fixtures_once(self):
        run_seed()
        self.assertTrue(User.objects.filter(username='minahil').exists())
        self.assertIn('skipping fixtures', run_seed())


@override_settings(CLOUDINARY_URL=CLOUDINARY)
@mock.patch('backend.storage.upload')
@mock.patch('cloudinary.api.resource')
@mock.patch('cloudinary.api.ping')
class SeedWithCloudinaryTests(TestCase):
    def test_bad_credentials_fail_before_touching_the_database(self, ping, resource, upload):
        ping.side_effect = cloudinary.exceptions.AuthorizationRequired('Invalid Signature')
        with self.assertRaisesMessage(CommandError, 'API secret revealed'):
            run_seed()
        self.assertFalse(User.objects.exists())
        upload.assert_not_called()

    def test_fresh_database_loads_fixtures_and_uploads_media(self, ping, resource, upload):
        run_seed()
        self.assertTrue(User.objects.exists())
        self.assertGreater(upload.call_count, 30)

    def test_recovers_when_data_loaded_but_media_missing(self, ping, resource, upload):
        # the situation after a deploy with a wrong API secret
        call_command('loaddata', *[f'fixtures/{n}.json' for n in (
            'User', 'Genre', 'Album', 'Song', 'Playlist', 'Track', 'UserData',
            'RecentlyPlayedAlbum', 'RecentlyPlayedPlaylist', 'UserAlbumLibrary',
            'UserArtistLibrary', 'UserPlaylistLibrary')], verbosity=0)
        resource.side_effect = cloudinary.exceptions.NotFound('not found')
        output = run_seed()
        self.assertIn('skipping fixtures', output)
        self.assertGreater(upload.call_count, 30)

    def test_does_nothing_when_data_and_media_exist(self, ping, resource, upload):
        run_seed()
        upload.reset_mock()
        output = run_seed()
        self.assertIn('already on Cloudinary', output)
        upload.assert_not_called()
