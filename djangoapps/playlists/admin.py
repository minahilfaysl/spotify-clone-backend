from django.contrib import admin
from djangoapps.playlists.models import Playlist, Track


admin.site.register(Playlist)
admin.site.register(Track)
