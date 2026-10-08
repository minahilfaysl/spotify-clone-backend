from django.db import models
from django.contrib.auth import get_user_model

from backend.images import crop_new_upload_to_square

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
        crop_new_upload_to_square(self.album_cover_photo)
        super().save(*args, **kwargs)


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
