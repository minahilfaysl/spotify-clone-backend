from django.db import models
from django.contrib.auth import get_user_model
from djangoapps.songs.models import Song, Album
from djangoapps.playlists.models import Playlist

User = get_user_model()


class RecentlyPlayedAlbum(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # an user can not have duplicate recently listened to album records
        unique_together = (('user', 'album'),)

    def __str__(self):
        return '%s: %s' % (self.user.profile_name, self.album.album_name)


class RecentlyPlayedPlaylist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # an user can not have duplicate recently listened to playlist records
        unique_together = (('user', 'playlist'),)

    def __str__(self):
        return '%s: %s' % (self.user.profile_name, self.playlist.playlist_name)


class UserArtistLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="artist"
    )
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # an user can not have duplicate recently listened to artist records
        unique_together = (('user', 'artist'),)

    def __str__(self):
        return '%s: %s' % (self.user.profile_name, self.artist.profile_name)


class UserAlbumLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # an user can not have duplicate liked artist records
        unique_together = (('user', 'album'),)

    def __str__(self):
        return '%s: %s' % (self.user.profile_name, self.album.album_name)


class UserPlaylistLibrary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        # an user can not have duplicate recently listened to playlist records
        unique_together = (('user', 'playlist'),)

    def __str__(self):
        return '%s: %s' % (self.user.profile_name, self.playlist.playlist_name)


class UserData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # liked data
    liked_albums = models.ManyToManyField(
        Album,
        blank=True,
        related_name='user_album_likes'
    )
    liked_songs = models.ManyToManyField(
        Song,
        blank=True,
        related_name='user_song_likes'
    )
    liked_playlists = models.ManyToManyField(
        Playlist,
        blank=True,
        related_name='user_playlist_likes'
    )
    # recently played data
    recently_played_albums = models.ManyToManyField(
        RecentlyPlayedAlbum,
        blank=True,
        related_name='recently_played_albums',
    )
    recently_played_playlists = models.ManyToManyField(
        RecentlyPlayedPlaylist,
        blank=True,
        related_name='recently_played_playlists',
    )
    # library
    artist_library = models.ManyToManyField(
        UserArtistLibrary,
        blank=True,
        related_name='artist_library',
    )
    playlist_library = models.ManyToManyField(
        UserPlaylistLibrary,
        blank=True,
        related_name='playlist_library',
    )
    album_library = models.ManyToManyField(
        UserAlbumLibrary,
        blank=True,
        related_name='album_library',
    )
    # follow data
    followers = models.ManyToManyField(
        User,
        blank=True,
        related_name='followers'
    )
    following = models.ManyToManyField(
        User,
        blank=True,
        related_name='following'
    )

    def __str__(self):
        return self.user.profile_name
