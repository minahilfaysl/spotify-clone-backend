from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):
    genre_name = models.CharField(max_length=200, unique=True)
    color = models.CharField(max_length=200)

    def __str__(self):
        return self.genre_name


class Album(models.Model):
    artist = models.ForeignKey(User, on_delete=models.CASCADE)
    album_name = models.CharField(max_length=200)
    album_publish_year = models.IntegerField()
    album_cover_photo = models.ImageField(
        default='default_cover_photo.jpg',
        upload_to='album_cover_photo')
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT)

    class Meta:
        # an artist can not have duplicate albums
        unique_together = (('artist', 'album_name'),)

    def __str__(self):
        return self.album_name

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.album_cover_photo.path)
        width, height = img.size

        if height > 400 or width > 400 or width != height:
            # crop the image
            if width == height:
                resized_image = img
            offset = int(abs(height-width)/2)
            if width > height:
                resized_image = img.crop([offset, 0, width-offset, height])
            else:
                resized_image = img.crop([0, offset, width, height-offset])

            # resize image and save
            output_size = (400, 400)
            resized_image.thumbnail(output_size)
            resized_image.save(self.album_cover_photo.path)


class Song(models.Model):
    song_name = models.CharField(max_length=200)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='audio_file', blank=True)
    duration = models.DurationField(blank=True, null=True)
    track_number = models.IntegerField()
    # disc_number = models.IntegerField(max_length=1)
    is_explicit = models.BooleanField(default=False)
    total_streams = models.IntegerField(default=0)

    class Meta:
        # an album can not have duplicate songs
        unique_together = (('album', 'song_name'), ('album', 'track_number'))

    def __str__(self):
        return self.song_name
