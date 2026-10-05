from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from djangoapps.songs.models import Song


User = get_user_model()


class Playlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist_name = models.CharField(max_length=200)
    description = models.TextField()
    playlist_cover_photo = models.ImageField(
        default='default_cover_photo.jpg',
        upload_to='playlist_cover_photo')
    is_private = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)

    # total_length: the total time of all tracks added to the playlist
    # TO-DO: update for adding and removing songs from playlist
    total_length = models.DurationField(blank=True, null=True)

    class Meta:
        # a user can not have duplicate playlists
        unique_together = (('user', 'playlist_name'),)

    def __str__(self):
        return self.playlist_name

    def save(self, *args, **kwargs):
        super().save()

        img = Image.open(self.playlist_cover_photo.path)
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
            resized_image.save(self.playlist_cover_photo.path)


class Track(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True, null=False)

    class Meta:
        ordering = ['date_added']

    def __str__(self):
        return '%s: %s' % (self.playlist.playlist_name, self.song.song_name)
