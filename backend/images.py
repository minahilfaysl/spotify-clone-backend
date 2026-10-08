from io import BytesIO

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

COVER_SIZE = 400


def crop_new_upload_to_square(field_file, size=COVER_SIZE):
    """Center-crop a newly uploaded image to a square of at most `size` px.

    Runs in memory before the file reaches storage, so it works with
    Cloudinary as well as local disk. Images already saved are left alone,
    so ordinary saves (e.g. updating last_login) don't touch the file.
    """
    if not field_file or getattr(field_file, '_committed', True):
        return

    upload = field_file.file
    upload.seek(0)
    original = Image.open(upload)
    image_format = original.format or 'JPEG'
    image = ImageOps.exif_transpose(original)

    width, height = image.size
    if width == height and width <= size:
        upload.seek(0)
        return

    side = min(width, height)
    left, top = (width - side) // 2, (height - side) // 2
    image = image.crop((left, top, left + side, top + side))
    image.thumbnail((size, size))

    if image_format == 'JPEG' and image.mode not in ('RGB', 'L'):
        image = image.convert('RGB')

    buffer = BytesIO()
    image.save(buffer, format=image_format)
    field_file.save(field_file.name, ContentFile(buffer.getvalue()), save=False)
