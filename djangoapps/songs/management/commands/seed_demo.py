from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = ('Load the demo fixtures and, when Cloudinary is configured, upload '
            'the demo media files. Does nothing if the database already has '
            'users, so it is safe to run on every deploy.')

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Seed even if the database already has users.')

    def handle(self, *args, force=False, **options):
        if get_user_model().objects.exists() and not force:
            self.stdout.write('Database already has data; skipping demo seed.')
            return

        fixtures = sorted(str(p) for p in Path(settings.BASE_DIR, 'fixtures').glob('*.json'))
        # One call so cross-fixture references resolve together.
        call_command('loaddata', *fixtures)

        if settings.CLOUDINARY_URL:
            self.upload_demo_media()

    def upload_demo_media(self):
        from backend.storage import upload

        media_root = Path(settings.MEDIA_ROOT)
        files = sorted(p for p in media_root.rglob('*') if p.is_file())
        for path in files:
            name = path.relative_to(media_root).as_posix()
            with path.open('rb') as fh:
                upload(fh, name)
            self.stdout.write(f'Uploaded {name}')
        self.stdout.write(self.style.SUCCESS(f'Uploaded {len(files)} media files to Cloudinary.'))
