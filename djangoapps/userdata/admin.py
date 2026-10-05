from django.contrib import admin
from djangoapps.userdata.models import (
    UserData,
    RecentlyPlayedAlbum,
    RecentlyPlayedPlaylist,
    UserArtistLibrary,
    UserAlbumLibrary,
    UserPlaylistLibrary,
)

admin.site.register(UserData)
admin.site.register(RecentlyPlayedAlbum)
admin.site.register(RecentlyPlayedPlaylist)
admin.site.register(UserArtistLibrary)
admin.site.register(UserAlbumLibrary)
admin.site.register(UserPlaylistLibrary)
