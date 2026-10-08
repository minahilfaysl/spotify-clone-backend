"""Django storage backend that keeps uploaded media on Cloudinary.

Enabled in settings when the CLOUDINARY_URL environment variable is set.
File names stay the same as with local storage (e.g. "audio_file/song.mp3"),
so database rows and fixtures work unchanged; Cloudinary public IDs are the
name without its extension, under the CLOUDINARY_FOLDER prefix.
"""
import os
import secrets

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

CLOUDINARY_FOLDER = os.environ.get('CLOUDINARY_FOLDER', 'spotify-clone')

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.avif'}
# Cloudinary stores audio under the "video" resource type.
AUDIO_VIDEO_EXTENSIONS = {'.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac', '.mp4', '.webm', '.mov'}


def resource_type_for(name):
    ext = os.path.splitext(name)[1].lower()
    if ext in IMAGE_EXTENSIONS:
        return 'image'
    if ext in AUDIO_VIDEO_EXTENSIONS:
        return 'video'
    return 'raw'


def public_id_for(name):
    """Map a Django file name to its Cloudinary public ID and format."""
    name = name.replace('\\', '/')
    root, ext = os.path.splitext(name)
    if resource_type_for(name) == 'raw':
        # Raw files keep their extension in the public ID.
        return f'{CLOUDINARY_FOLDER}/{name}', None
    return f'{CLOUDINARY_FOLDER}/{root}', ext.lstrip('.').lower() or None


def upload(content, name):
    """Upload a file object to Cloudinary under the public ID for `name`."""
    public_id, _ = public_id_for(name)
    if hasattr(content, 'seek'):
        content.seek(0)
    return cloudinary.uploader.upload(
        content,
        public_id=public_id,
        resource_type=resource_type_for(name),
        overwrite=True,
        unique_filename=False,
        invalidate=True,
    )


@deconstructible
class CloudinaryMediaStorage(Storage):

    def _save(self, name, content):
        upload(content, name)
        return name.replace('\\', '/')

    def _open(self, name, mode='rb'):
        raise NotImplementedError(
            'Media lives on Cloudinary; read it through storage.url(name).')

    def get_available_name(self, name, max_length=None):
        # Add a short random suffix instead of asking Cloudinary whether the
        # name is taken (saves an API call per upload).
        root, ext = os.path.splitext(name)
        candidate = f'{root}_{secrets.token_hex(4)}{ext}'
        if max_length and len(candidate) > max_length:
            root = root[:max_length - len(ext) - 9]
            candidate = f'{root}_{secrets.token_hex(4)}{ext}'
        return candidate

    def exists(self, name):
        return False

    def delete(self, name):
        if not name:
            return
        public_id, _ = public_id_for(name)
        cloudinary.uploader.destroy(
            public_id, resource_type=resource_type_for(name), invalidate=True)

    def url(self, name):
        public_id, fmt = public_id_for(name)
        options = {'resource_type': resource_type_for(name), 'secure': True}
        if fmt:
            options['format'] = fmt
        return cloudinary.utils.cloudinary_url(public_id, **options)[0]
