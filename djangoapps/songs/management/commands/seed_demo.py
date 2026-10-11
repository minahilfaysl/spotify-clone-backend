from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = ('Load the demo fixtures into an empty database and, when Cloudinary '
            'is configured, make sure the demo media files are uploaded. Safe '
            'to run on every deploy.')

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Reload fixtures and re-upload media even if they exist.')

    def handle(self, *args, force=False, **options):
        use_cloudinary = bool(settings.CLOUDINARY_URL)
        if use_cloudinary:
            # Check credentials before touching the database, so a typo in
            # CLOUDINARY_URL can't leave demo data loaded without its media.
            self.check_cloudinary_credentials()

        if force or not get_user_model().objects.exists():
            fixtures = sorted(str(p) for p in Path(settings.BASE_DIR, 'fixtures').glob('*.json'))
            # One call so cross-fixture references resolve together.
            call_command('loaddata', *fixtures)
            needs_media = True
        else:
            self.stdout.write('Database already has data; skipping fixtures.')
            # A previous deploy may have loaded the data but failed to upload
            # the media (e.g. wrong credentials), so check rather than assume.
            needs_media = use_cloudinary and not self.demo_media_uploaded()

        if use_cloudinary and needs_media:
            self.upload_demo_media()
        elif use_cloudinary:
            self.stdout.write('Demo media already on Cloudinary; skipping upload.')

    def demo_media_files(self):
        media_root = Path(settings.MEDIA_ROOT)
        return [(path, path.relative_to(media_root).as_posix())
                for path in sorted(p for p in media_root.rglob('*') if p.is_file())]

    def check_cloudinary_credentials(self):
        import cloudinary.api
        import cloudinary.exceptions

        try:
            cloudinary.api.ping()
        except cloudinary.exceptions.Error as exc:
            raise CommandError(
                f'Cloudinary rejected the credentials in CLOUDINARY_URL ({exc}). '
                'Copy the "API environment variable" from the Cloudinary dashboard '
                'with the API secret revealed, and paste only the part starting '
                'with cloudinary:// (no "CLOUDINARY_URL=", quotes or spaces).'
            ) from exc

    def demo_media_uploaded(self):
        '''True if the last demo file is on Cloudinary (uploads go in order).'''
        import cloudinary.api
        import cloudinary.exceptions
        from backend.storage import public_id_for, resource_type_for

        files = self.demo_media_files()
        if not files:
            return True
        _, name = files[-1]
        public_id, _ = public_id_for(name)
        try:
            cloudinary.api.resource(public_id, resource_type=resource_type_for(name))
            return True
        except cloudinary.exceptions.NotFound:
            return False

    def upload_demo_media(self):
        from backend.storage import upload

        files = self.demo_media_files()
        for path, name in files:
            with path.open('rb') as fh:
                upload(fh, name)
            self.stdout.write(f'Uploaded {name}')
        self.stdout.write(self.style.SUCCESS(f'Uploaded {len(files)} media files to Cloudinary.'))
