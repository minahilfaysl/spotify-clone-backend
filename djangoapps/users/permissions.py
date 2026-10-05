from rest_framework.permissions import BasePermission, SAFE_METHODS

from djangoapps.songs.models import Album


class IsArtist(BasePermission):
    '''
    for checking if a user is an artist when creating or editing songs and
    albums
    '''

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        permission = request.user.is_artist and request.user.is_authenticated
        return permission

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        try:
            # for albums
            artist = obj.artist
        except AttributeError:
            # for songs
            album_obj = Album.objects.filter(id=obj.album.id).first()
            artist = album_obj.artist

        return artist == request.user
